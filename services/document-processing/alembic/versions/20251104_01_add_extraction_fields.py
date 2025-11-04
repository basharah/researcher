"""add extraction fields to documents

Revision ID: 20251104_01
Revises: 
Create Date: 2025-11-04 21:50:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20251104_01'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add JSONB columns
    op.add_column('documents', sa.Column('tables_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('documents', sa.Column('figures_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('documents', sa.Column('references_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True))

    # Add boolean flags with default False
    op.add_column('documents', sa.Column('tables_extracted', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    op.add_column('documents', sa.Column('figures_extracted', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    op.add_column('documents', sa.Column('references_extracted', sa.Boolean(), nullable=False, server_default=sa.text('false')))


def downgrade() -> None:
    op.drop_column('documents', 'references_extracted')
    op.drop_column('documents', 'figures_extracted')
    op.drop_column('documents', 'tables_extracted')
    op.drop_column('documents', 'references_json')
    op.drop_column('documents', 'figures_metadata')
    op.drop_column('documents', 'tables_data')
