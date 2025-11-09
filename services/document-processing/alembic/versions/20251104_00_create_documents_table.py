"""create documents table

Revision ID: 20251104_00
Revises: 
Create Date: 2025-11-04 20:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20251104_00'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create documents table
    op.create_table(
        'documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('filename', sa.String(), nullable=True),
        sa.Column('original_filename', sa.String(), nullable=True),
        sa.Column('file_path', sa.String(), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('page_count', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('authors', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('publication_date', sa.String(), nullable=True),
        sa.Column('doi', sa.String(), nullable=True),
        sa.Column('abstract', sa.Text(), nullable=True),
        sa.Column('introduction', sa.Text(), nullable=True),
        sa.Column('methodology', sa.Text(), nullable=True),
        sa.Column('results', sa.Text(), nullable=True),
        sa.Column('conclusion', sa.Text(), nullable=True),
        sa.Column('references', sa.Text(), nullable=True),
        sa.Column('full_text', sa.Text(), nullable=True),
        sa.Column('upload_date', sa.DateTime(), nullable=True),
        sa.Column('processed_date', sa.DateTime(), nullable=True),
        sa.Column('processing_status', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_documents_id'), 'documents', ['id'], unique=False)
    op.create_index(op.f('ix_documents_filename'), 'documents', ['filename'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_documents_filename'), table_name='documents')
    op.drop_index(op.f('ix_documents_id'), table_name='documents')
    op.drop_table('documents')
