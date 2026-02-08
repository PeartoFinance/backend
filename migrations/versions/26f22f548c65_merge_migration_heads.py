"""merge_migration_heads

Revision ID: 26f22f548c65
Revises: 3498e773c4a8, d4e5f6a7b8c9
Create Date: 2026-02-08 09:09:35.430345

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '26f22f548c65'
down_revision = ('3498e773c4a8', 'd4e5f6a7b8c9')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
