"""Add room_id column to orders table

Revision ID: 2aae965676de
Revises: 65a1829d32d0
Create Date: 2023-12-26 02:04:19.125293

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session

# revision identifiers, used by Alembic.
revision: str = "2aae965676de"
down_revision: Union[str, None] = "65a1829d32d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("orders", sa.Column("room_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "orders_room_id_fkey", "orders", "rooms", ["room_id"], ["id"], onupdate="CASCADE", ondelete="CASCADE"
    )

    # copy room_id values from `tasks` table to `orders` table
    with Session(bind=op.get_bind()) as session:
        # noinspection PyUnresolvedReferences
        pairs = session.execute(
            sa.select(sa.column("order_id"), sa.column("room_id"))
            .select_from(sa.table("tasks"))
            .where(sa.column("order_id").isnot(None))
        ).fetchall()

        data = {}
        for order_id, room_id in pairs:
            # Also removes possible duplicates (one order - many rooms). Should not be a real case.
            data[order_id] = room_id
        if data:
            session.execute(
                sa.update(sa.table("orders", sa.column("room_id")))
                .where(sa.column("id") == sa.bindparam("order_id"))
                .values(room_id=sa.bindparam("room_id")),
                [{"order_id": order_id, "room_id": room_id} for order_id, room_id in data.items()],
                execution_options={"synchronize_session": None},
            )

        # "garbage collection". Should do nothing.
        # Removes orders that are not referenced by any room.
        session.execute(sa.delete(sa.table("orders")).where(sa.column("room_id").is_(None)))

    op.alter_column("orders", "room_id", nullable=False)


def downgrade() -> None:
    op.drop_constraint("orders_room_id_fkey", "orders", type_="foreignkey")
    op.drop_column("orders", "room_id")

    # "garbage collection". Should do nothing.
    # Removes orders that are not referenced by any room.
    with Session(bind=op.get_bind()) as session:
        garbage = (
            session.execute(
                sa.select(sa.column("order_id"))
                .select_from(sa.table("tasks"))
                .where(sa.column("order_id").isnot(None))
                .distinct()
            )
            .scalars()
            .fetchall()
        )
        session.execute(sa.delete(sa.table("orders")).where(sa.column("id").notin_(garbage)))
