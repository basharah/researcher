"""Generic single-database configuration.

Revision ID: 260c02d7adf5
Revises: 20251110_01_processing_jobs
Create Date: 2025-11-10 14:14:13.067070

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '260c02d7adf5'
down_revision: Union[str, None] = '20251110_01_processing_jobs'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename metadata column to job_metadata in processing_jobs table
    op.alter_column('processing_jobs', 'metadata', new_column_name='job_metadata')


def downgrade() -> None:
    # Rename job_metadata back to metadata
    op.alter_column('processing_jobs', 'job_metadata', new_column_name='metadata')
