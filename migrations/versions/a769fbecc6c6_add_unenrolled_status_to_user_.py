"""add unenrolled status to user_enrollments

Revision ID: a769fbecc6c6
Revises: 2d2049edf8e1
Create Date: 2026-01-13 20:48:25.098436

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a769fbecc6c6'
down_revision = '2d2049edf8e1'
branch_labels = None
depends_on = None


def upgrade():
   op.execute("""
        ALTER TABLE user_enrollments
        MODIFY COLUMN status
        ENUM('enrolled','in_progress','paused','completed','unenrolled')
        NOT NULL
    """)


def downgrade():
    op.execute("""
        ALTER TABLE user_enrollments
        MODIFY COLUMN status
        ENUM('enrolled','in_progress','paused','completed')
        NOT NULL
    """)
