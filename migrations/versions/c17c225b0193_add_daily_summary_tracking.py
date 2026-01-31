"""add_daily_summary_tracking

Revision ID: c17c225b0193
Revises: 82e30db52b46
Create Date: 2026-01-31 16:50:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c17c225b0193'
down_revision = '82e30db52b46'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Add email_portfolio_summary column to user_notification_prefs
    op.add_column('user_notification_prefs', sa.Column('email_portfolio_summary', sa.Boolean(), server_default='1', nullable=True))

    # 2. Create daily_summary_notifications table
    op.create_table(
        'daily_summary_notifications',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'date', name='ux_user_daily_summary_date'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], )
    )


def downgrade():
    op.drop_table('daily_summary_notifications')
    op.drop_column('user_notification_prefs', 'email_portfolio_summary')
