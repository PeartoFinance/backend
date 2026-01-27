"""create news_preferences and news_notifications tables

Revision ID: 20260127_001_create_news_tables
Revises: f6138add059d
Create Date: 2026-01-27 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260127_001_create_news_tables'
down_revision = 'f6138add059d'
branch_labels = None
depends_on = None


def upgrade():
    # Create news_preferences table
    op.create_table(
        'news_preferences',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('companies', sa.JSON(), nullable=True),
        sa.Column('categories', sa.JSON(), nullable=True),
        sa.Column('news_type', sa.Enum('company', 'independent'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )

    # Create news_notifications table
    op.create_table(
        'news_notifications',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('news_id', sa.Integer(), nullable=False),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'news_id', name='ux_user_news_notification')
    )


def downgrade():
    # Drop tables
    op.drop_table('news_notifications')
    op.drop_table('news_preferences')
