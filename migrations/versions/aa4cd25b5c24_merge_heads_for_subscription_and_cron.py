"""Merge heads for subscription and cron

Revision ID: aa4cd25b5c24
Revises: 4fc37e151cbb, 6b22f8c8714f
Create Date: 2026-02-06 15:03:10.573910

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'aa4cd25b5c24'
down_revision = ('4fc37e151cbb', '6b22f8c8714f')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
