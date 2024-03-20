"""Rename User.telegram_id -> User.id

Revision ID: c365f238a8d2
Revises: 859c79cfe1b5
Create Date: 2023-12-22 18:47:47.363441

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "c365f238a8d2"
down_revision: Union[str, None] = "859c79cfe1b5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("users", "telegram_id", new_column_name="id")


def downgrade() -> None:
    op.alter_column("users", "id", new_column_name="telegram_id")
