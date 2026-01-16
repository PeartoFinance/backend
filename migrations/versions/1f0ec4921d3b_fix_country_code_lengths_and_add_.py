"""fix_country_code_lengths_and_add_commodity_column

Revision ID: 1f0ec4921d3b
Revises: 3258a0ecda16
Create Date: 2026-01-16 10:26:27.892742

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1f0ec4921d3b'
down_revision = '3258a0ecda16'
branch_labels = None
depends_on = None


def upgrade():
    # Fix country_code lengths to 10 to accommodate 'GLOBAL'
    op.execute("ALTER TABLE market_data MODIFY COLUMN country_code VARCHAR(10)")
    op.execute("ALTER TABLE market_indices MODIFY COLUMN country_code VARCHAR(10)")
    op.execute("ALTER TABLE dividends MODIFY COLUMN country_code VARCHAR(10)")
    op.execute("ALTER TABLE bulk_transactions MODIFY COLUMN country_code VARCHAR(10)")
    
    # Add country_code to commodities_data
    op.execute("ALTER TABLE commodities_data ADD COLUMN country_code VARCHAR(10) DEFAULT 'GLOBAL'")


def downgrade():
    # Revert country_code lengths
    op.execute("ALTER TABLE market_data MODIFY COLUMN country_code VARCHAR(2)")
    op.execute("ALTER TABLE market_indices MODIFY COLUMN country_code VARCHAR(5)")
    op.execute("ALTER TABLE dividends MODIFY COLUMN country_code VARCHAR(5)")
    op.execute("ALTER TABLE bulk_transactions MODIFY COLUMN country_code VARCHAR(5)")
    
    # Remove country_code from commodities_data
    op.execute("ALTER TABLE commodities_data DROP COLUMN country_code")
