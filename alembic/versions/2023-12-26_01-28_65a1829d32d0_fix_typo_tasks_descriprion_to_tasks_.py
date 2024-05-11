"""fix typo tasks.descriprion to tasks.description

Revision ID: 65a1829d32d0
Revises: e0547a6dc25d
Create Date: 2023-12-26 01:17:30.301242

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "65a1829d32d0"
down_revision: Union[str, None] = "e0547a6dc25d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("tasks", "descriprion", new_column_name="description")


def downgrade() -> None:
    op.alter_column("tasks", "description", new_column_name="descriprion")
