"""fix typo invitations.adressee_id to invitations.addressee_id

Revision ID: 6d339f52f632
Revises: 2aae965676de
Create Date: 2024-01-02 04:12:54.644738

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "6d339f52f632"
down_revision: Union[str, None] = "2aae965676de"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("invitations", "adressee_id", new_column_name="addressee_id")


def downgrade() -> None:
    op.alter_column("invitations", "addressee_id", new_column_name="adressee_id")
