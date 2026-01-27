"""add unique constraint on user_notification_prefs.user_id

Revision ID: add_user_notif_unique
Revises: 20260127_001_create_news_tables
Create Date: 2026-01-27 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_user_notif_unique'
down_revision = '20260127_001_create_news_tables'
branch_labels = None
depends_on = None


def upgrade():
    # Add unique constraint on user_id in user_notification_prefs
    with op.batch_alter_table('user_notification_prefs', schema=None) as batch_op:
        batch_op.create_unique_constraint('ux_user_notification_prefs_user_id', ['user_id'])


def downgrade():
    # Drop the unique constraint
    with op.batch_alter_table('user_notification_prefs', schema=None) as batch_op:
        batch_op.drop_constraint('ux_user_notification_prefs_user_id', type_='unique')
