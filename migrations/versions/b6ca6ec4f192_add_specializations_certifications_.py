"""Add specializations, certifications, hourly_rate to users

Revision ID: b6ca6ec4f192
Revises: 26f22f548c65
Create Date: 2026-02-08 09:10:40.709552

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'b6ca6ec4f192'
down_revision = '26f22f548c65'
branch_labels = None
depends_on = None


def upgrade():
    # Add profile customization columns to users table
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('specializations', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('certifications', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('hourly_rate', sa.Numeric(precision=10, scale=2), nullable=True))


def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('hourly_rate')
        batch_op.drop_column('certifications')
        batch_op.drop_column('specializations')
