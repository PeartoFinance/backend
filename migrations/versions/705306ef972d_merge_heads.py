"""Merge heads

Revision ID: 705306ef972d
Revises: add_page_placement, c17c225b0193
Create Date: 2026-02-04 08:56:01.374786

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '705306ef972d'
down_revision = ('add_page_placement', 'c17c225b0193')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
