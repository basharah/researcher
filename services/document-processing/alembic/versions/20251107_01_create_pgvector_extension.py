"""create pgvector extension

Revision ID: 20251107_01
Revises: 20251104_01
Create Date: 2025-11-07 18:00:00

"""
from alembic import op
from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = '20251107_01'
down_revision: Union[str, None] = '20251104_01'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Ensure pgvector extension exists before any Vector columns are created
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")


def downgrade() -> None:
    # Leave the extension in place by default; if you want to remove it uncomment below
    # op.execute("DROP EXTENSION IF EXISTS vector;")
    pass
