"""Allow one user to repeat within on order

Revision ID: e0547a6dc25d
Revises: c365f238a8d2
Create Date: 2023-12-25 00:47:29.406628

"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import delete, table, select, func, exists, column
from sqlalchemy.orm import Session

# revision identifiers, used by Alembic.
revision: str = "e0547a6dc25d"
down_revision: Union[str, None] = "c365f238a8d2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("executors", "order_number", autoincrement=False)
    op.drop_constraint("executors_pkey", "executors", type_="primary")
    op.create_primary_key("executors_pkey", "executors", ["user_id", "order_id", "order_number"])


def downgrade() -> None:
    with Session(bind=op.get_bind()) as db:
        orders_table = table("orders", column("id"))
        db.execute(
            delete(orders_table).where(
                exists(
                    select(column("user_id"))
                    .select_from(table("executors"))
                    .where(column("order_id") == orders_table.c.id)
                    .group_by(column("user_id"))
                    .having(func.count() >= 2)
                )
            )
        )
    op.alter_column("executors", "order_number", autoincrement=False)
    op.drop_constraint("executors_pkey", "executors", type_="primary")
    op.create_primary_key("executors_pkey", "executors", ["user_id", "order_id"])
