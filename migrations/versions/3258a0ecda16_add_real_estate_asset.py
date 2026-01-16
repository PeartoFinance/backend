"""add real estate asset

Revision ID: 3258a0ecda16
Revises: a769fbecc6c6
Create Date: 2026-01-16 00:14:45.470431

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3258a0ecda16"
down_revision = "a769fbecc6c6"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        ALTER TABLE market_data
        MODIFY COLUMN asset_type
        ENUM('stock', 'crypto', 'forex', 'commodity', 'index', 'etf')
        NOT NULL
        DEFAULT 'stock'
    """)


def downgrade():
    op.execute("""
        ALTER TABLE market_data
        MODIFY COLUMN asset_type
        ENUM('stock', 'crypto', 'forex', 'commodity', 'index')
        NOT NULL
        DEFAULT 'stock'
    """)
