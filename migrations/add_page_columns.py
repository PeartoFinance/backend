"""
Migration to add new Page model columns.
Run this to add placement, featured_image, author_id, sort_order columns to pages table.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db

def migrate():
    """Add new columns to pages table"""
    app = create_app()
    with app.app_context():
        # Check if columns exist and add them if not
        migrations = [
            "ALTER TABLE pages ADD COLUMN IF NOT EXISTS placement VARCHAR(100) DEFAULT 'none'",
            "ALTER TABLE pages ADD COLUMN IF NOT EXISTS featured_image VARCHAR(500)",
            "ALTER TABLE pages ADD COLUMN IF NOT EXISTS author_id INT",
            "ALTER TABLE pages ADD COLUMN IF NOT EXISTS sort_order INT DEFAULT 0",
        ]
        
        for sql in migrations:
            try:
                db.session.execute(db.text(sql))
                print(f"Executed: {sql[:50]}...")
            except Exception as e:
                # Column might already exist or different SQL syntax needed
                print(f"Note: {e}")
        
        db.session.commit()
        print("\nMigration completed successfully!")

if __name__ == '__main__':
    migrate()
