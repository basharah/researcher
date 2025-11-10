"""Add processing jobs and DOI fields

Revision ID: 20251110_01_processing_jobs
Revises: 20251104_01_add_extraction_fields
Create Date: 2025-11-10 13:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20251110_01_processing_jobs'
down_revision = '20251107_01'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create processing_jobs table
    op.create_table(
        'processing_jobs',
        sa.Column('job_id', sa.String(36), primary_key=True),
        sa.Column('batch_id', sa.String(36), nullable=True, index=True),
        sa.Column('document_id', sa.Integer, sa.ForeignKey('documents.id', ondelete='CASCADE'), nullable=True),
        sa.Column('filename', sa.String(500), nullable=False),
        sa.Column('file_size', sa.Integer, nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending', index=True),
        sa.Column('progress', sa.Integer, nullable=False, server_default='0'),  # 0-100
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('started_at', sa.DateTime, nullable=True),
        sa.Column('completed_at', sa.DateTime, nullable=True),
        sa.Column('user_id', sa.String(36), nullable=True, index=True),
        sa.Column('metadata', postgresql.JSONB, nullable=True),
    )
    # Create processing_steps table for detailed logging
    op.create_table(
        'processing_steps',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('job_id', sa.String(36), sa.ForeignKey('processing_jobs.job_id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('step_name', sa.String(100), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),  # started, completed, failed
        sa.Column('message', sa.Text, nullable=True),
        sa.Column('started_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('completed_at', sa.DateTime, nullable=True),
        sa.Column('duration_ms', sa.Integer, nullable=True),
        sa.Column('details', postgresql.JSONB, nullable=True),
    )

        # Add new columns to documents table (only if they don't exist)
    conn = op.get_bind()
    
    # Check existing columns
    existing_columns = conn.execute(
        sa.text("SELECT column_name FROM information_schema.columns WHERE table_name = 'documents'")
    ).fetchall()
    existing_column_names = [row[0] for row in existing_columns]
    
    # Add columns only if they don't exist
    if 'batch_id' not in existing_column_names:
        op.add_column('documents', sa.Column('batch_id', sa.String(36), nullable=True, index=True))
    
    if 'processing_job_id' not in existing_column_names:
        op.add_column('documents', sa.Column('processing_job_id', sa.String(36), nullable=True))
    
    if 'ocr_applied' not in existing_column_names:
        op.add_column('documents', sa.Column('ocr_applied', sa.Boolean, nullable=False, server_default='false'))
    
    # Add foreign key constraint if it doesn't exist
    existing_constraints = conn.execute(
        sa.text("SELECT constraint_name FROM information_schema.table_constraints WHERE table_name = 'documents'")
    ).fetchall()
    constraint_names = [row[0] for row in existing_constraints]
    
    if 'fk_documents_processing_job' not in constraint_names:
        op.create_foreign_key(
            'fk_documents_processing_job',
            'documents', 'processing_jobs',
            ['processing_job_id'], ['job_id'],
            ondelete='SET NULL'
        )



def downgrade() -> None:
    # Drop foreign key and new columns from documents
    op.drop_constraint('fk_documents_processing_job', 'documents', type_='foreignkey')
    op.drop_column('documents', 'processing_job_id')
    op.drop_column('documents', 'ocr_applied')
    op.drop_column('documents', 'batch_id')
    op.drop_column('documents', 'doi')
    
    # Drop tables
    op.drop_table('processing_steps')
    op.drop_table('processing_jobs')
