"""Add trial fields to subscription plans

Revision ID: d4e5f6a7b8c9
Revises: aa4cd25b5c24
Create Date: 2026-02-08 07:50:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd4e5f6a7b8c9'
down_revision = 'aa4cd25b5c24'
branch_labels = None
depends_on = None


def upgrade():
    # Add trial_enabled and trial_days columns to subscription_plans
    op.add_column('subscription_plans', 
        sa.Column('trial_enabled', sa.Boolean(), nullable=True, default=False)
    )
    op.add_column('subscription_plans', 
        sa.Column('trial_days', sa.Integer(), nullable=True, default=7)
    )
    
    # Set default values for existing rows
    op.execute("UPDATE subscription_plans SET trial_enabled = 0, trial_days = 7 WHERE trial_enabled IS NULL")


def downgrade():
    op.drop_column('subscription_plans', 'trial_days')
    op.drop_column('subscription_plans', 'trial_enabled')
