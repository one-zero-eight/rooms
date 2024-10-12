"""Separate orders for tasks

Revision ID: 88e673b84a4c
Revises: 0ebe95bd6b25
Create Date: 2024-10-13 01:30:18.842558

"""
from collections import defaultdict
from typing import Sequence, Union

from alembic import op
from sqlalchemy import select, table, column, insert, update
from sqlalchemy.orm import Session

# revision identifiers, used by Alembic.
revision: str = "88e673b84a4c"
down_revision: Union[str, None] = "0ebe95bd6b25"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def fetch_order_data(s: Session, order_id: int):
    order_data = s.execute(
        select(column("room_id"))
        .select_from(table("orders"))
        .where(column("id") == order_id)
    ).one()
    executors = s.execute(
        select(column("user_id"), column("order_number"))
        .select_from(table("executors"))
        .where(column("order_id") == order_id)
    ).all()
    return order_data, executors


def clone_order(s: Session, order_data, executors):
    new_order_id = s.scalar(
        insert(table("orders", column('room_id')))
        .values(room_id=order_data[0])
        .returning(column('id'))
    )
    s.execute(
        insert(table("executors", column("user_id"), column("order_id"), column("order_number")))
        .values(order_id=new_order_id),
        [{"user_id": e[0], "order_number": e[1]} for e in executors]
    )
    return new_order_id


def upgrade() -> None:
    with Session(bind=op.get_bind()) as session:
        periodic_tasks: defaultdict[int, list[int]] = defaultdict(list)
        pairs = session.execute(
            select(column("id"), column("order_id"))
            .select_from(table("tasks"))
            .where(column("order_id").isnot(None))
        ).all()
        for task_id, order_id in pairs:
            periodic_tasks[order_id].append(task_id)
        for order_id, tasks in periodic_tasks.items():
            if len(tasks) == 1:
                continue
            order_data, executors = fetch_order_data(session, order_id)
            for task_id in tasks[1:]:
                new_order_id = clone_order(session, order_data, executors)
                # link
                session.execute(
                    update(table("tasks", column("order_id")))
                    .values(order_id=new_order_id)
                    .where(column("id") == task_id)
                )
        
        # same for manual tasks
        manual_tasks: defaultdict[int, list[int]] = defaultdict(list)
        pairs = session.execute(
            select(column("id"), column("order_id"))
            .select_from(table("manual_tasks"))
            .where(column("order_id").isnot(None))
        ).all()
        for task_id, order_id in pairs:
            manual_tasks[order_id].append(task_id)
        for order_id, tasks in manual_tasks.items():
            if len(tasks) == 1:
                continue
            order_data, executors = fetch_order_data(session, order_id)
            for task_id in tasks[1:]:
                new_order_id = clone_order(session, order_data, executors)
                # link
                session.execute(
                    update(table("manual_tasks", column("order_id")))
                    .values(order_id=new_order_id)
                    .where(column("id") == task_id)
                )


def downgrade() -> None:
    # No reverse actions are needed
    pass
