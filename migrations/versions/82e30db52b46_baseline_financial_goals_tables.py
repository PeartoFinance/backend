"""baseline financial goals tables

Revision ID: 82e30db52b46
Revises: 190542071fa7
Create Date: 2026-01-31 01:16:48.106747

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '82e30db52b46'
down_revision = '190542071fa7'
branch_labels = None
depends_on = None

def upgrade():
    # ---- financial_goals ----
    op.execute("""
    CREATE TABLE IF NOT EXISTS financial_goals (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        portfolio_id VARCHAR(255),
        target_amount DECIMAL(18,2) NOT NULL,
        start_amount DECIMAL(18,2) NOT NULL,
        target_date DATE NOT NULL,
        status ENUM('active','achieved','expired') DEFAULT 'active',
        notify_on_reach BOOLEAN DEFAULT TRUE,
        last_checked_at DATETIME,
        created_at DATETIME,
        updated_at DATETIME,
        INDEX idx_fin_goal_user (user_id),
        CONSTRAINT fk_fin_goal_user FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)

    # ---- financial_goal_notifications ----
    op.execute("""
    CREATE TABLE IF NOT EXISTS financial_goal_notifications (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        goal_id INT NOT NULL,
        sent_at DATETIME,
        UNIQUE KEY ux_user_goal_notification (user_id, goal_id),
        CONSTRAINT fk_goal_notif_user FOREIGN KEY (user_id) REFERENCES users(id),
        CONSTRAINT fk_goal_notif_goal FOREIGN KEY (goal_id) REFERENCES financial_goals(id)
    )
    """)


def downgrade():
    # ⚠️ DO NOT drop tables automatically in prod
    pass