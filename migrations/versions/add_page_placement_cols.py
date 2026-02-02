"""Add page placement columns

Revision ID: add_page_placement
Revises: 
Create Date: 2026-02-02

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_page_placement'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns to pages table with proper null handling
    with op.batch_alter_table('pages', schema=None) as batch_op:
        batch_op.add_column(sa.Column('placement', sa.String(length=100), server_default='none', nullable=True))
        batch_op.add_column(sa.Column('featured_image', sa.String(length=500), nullable=True))
        batch_op.add_column(sa.Column('author_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('sort_order', sa.Integer(), server_default='0', nullable=True))


def downgrade():
    with op.batch_alter_table('pages', schema=None) as batch_op:
        batch_op.drop_column('sort_order')
        batch_op.drop_column('author_id')
        batch_op.drop_column('featured_image')
        batch_op.drop_column('placement')
