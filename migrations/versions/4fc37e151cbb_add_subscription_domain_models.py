"""Add subscription domain models

Revision ID: 4fc37e151cbb
Revises: 5dff52ba91fb
Create Date: 2026-02-03 18:58:51.909862

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4fc37e151cbb'
down_revision = '5dff52ba91fb'
branch_labels = None
depends_on = None


def upgrade():
    pass
    # --- Commands to create the 4 new Subscription tables ---
    
    # op.create_table('subscription_plans',
    #     sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    #     sa.Column('name', sa.String(length=100), nullable=False),
    #     sa.Column('description', sa.Text(), nullable=True),
    #     sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False),
    #     sa.Column('currency', sa.String(length=3), nullable=True),
    #     sa.Column('interval', sa.String(length=20), nullable=True),
    #     sa.Column('duration_days', sa.Integer(), nullable=True),
    #     sa.Column('features', sa.JSON(), nullable=True),
    #     sa.Column('max_members', sa.Integer(), nullable=True),
    #     sa.Column('is_active', sa.Boolean(), nullable=True),
    #     sa.Column('is_featured', sa.Boolean(), nullable=True),
    #     sa.Column('created_at', sa.DateTime(), nullable=True),
    #     sa.Column('updated_at', sa.DateTime(), nullable=True),
    #     sa.PrimaryKeyConstraint('id')
    # )

    # op.create_table('subscription_coupons',
    #     sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    #     sa.Column('code', sa.String(length=50), nullable=False),
    #     sa.Column('discount_type', sa.String(length=20), nullable=True),
    #     sa.Column('discount_value', sa.Numeric(precision=10, scale=2), nullable=False),
    #     sa.Column('valid_from', sa.DateTime(), nullable=True),
    #     sa.Column('valid_until', sa.DateTime(), nullable=True),
    #     sa.Column('max_redemptions', sa.Integer(), nullable=True),
    #     sa.Column('times_redeemed', sa.Integer(), nullable=True),
    #     sa.Column('is_active', sa.Boolean(), nullable=True),
    #     sa.Column('created_at', sa.DateTime(), nullable=True),
    #     sa.PrimaryKeyConstraint('id'),
    #     sa.UniqueConstraint('code')
    # )

    # op.create_table('user_subscriptions',
    #     sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    #     sa.Column('user_id', sa.Integer(), nullable=False),
    #     sa.Column('plan_id', sa.Integer(), nullable=False),
    #     sa.Column('status', sa.String(length=20), nullable=True),
    #     sa.Column('auto_renew', sa.Boolean(), nullable=True),
    #     sa.Column('start_date', sa.DateTime(), nullable=True),
    #     sa.Column('current_period_end', sa.DateTime(), nullable=False),
    #     sa.Column('cancelled_at', sa.DateTime(), nullable=True),
    #     sa.Column('payment_gateway', sa.String(length=50), nullable=True),
    #     sa.Column('external_subscription_id', sa.String(length=100), nullable=True),
    #     sa.Column('created_at', sa.DateTime(), nullable=True),
    #     sa.ForeignKeyConstraint(['plan_id'], ['subscription_plans.id'], ),
    #     sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    #     sa.PrimaryKeyConstraint('id')
    # )

    # op.create_table('payment_transactions',
    #     sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    #     sa.Column('user_id', sa.Integer(), nullable=False),
    #     sa.Column('subscription_id', sa.Integer(), nullable=True),
    #     sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
    #     sa.Column('currency', sa.String(length=3), nullable=True),
    #     sa.Column('status', sa.String(length=20), nullable=False),
    #     sa.Column('gateway', sa.String(length=50), nullable=False),
    #     sa.Column('gateway_transaction_id', sa.String(length=100), nullable=True),
    #     sa.Column('description', sa.String(length=255), nullable=True),
    #     sa.Column('created_at', sa.DateTime(), nullable=True),
    #     sa.ForeignKeyConstraint(['subscription_id'], ['user_subscriptions.id'], ),
    #     sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    #     sa.PrimaryKeyConstraint('id')
    # )


def downgrade():
    op.drop_table('payment_transactions')
    op.drop_table('user_subscriptions')
    op.drop_table('subscription_coupons')
    op.drop_table('subscription_plans')
