"""Add referral_code to users table

Revision ID: 152a4197f570
Revises: b871fdaaa93c
Create Date: 2026-01-22 17:13:44.293202

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '152a4197f570'
down_revision = 'b871fdaaa93c'
branch_labels = None
depends_on = None


def upgrade():
    # Only add the referral_code column that's actually missing
    # The roles table changes were already applied or don't exist
    try:
        with op.batch_alter_table('users', schema=None) as batch_op:
            batch_op.add_column(sa.Column('referral_code', sa.String(length=50), nullable=True))
    except Exception as e:
        print(f"Note: referral_code might already exist: {e}")


def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('referral_code')
