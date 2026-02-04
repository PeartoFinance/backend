"""Merge migration heads

Revision ID: 5dff52ba91fb
Revises: add_page_placement, c17c225b0193
Create Date: 2026-02-03 18:54:07.627990

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5dff52ba91fb'
down_revision = ('add_page_placement', 'c17c225b0193')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
