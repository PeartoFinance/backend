"""
Migration Runner: Add Notification Preferences
Run this script to apply the notification preferences migration.
"""
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import app
from models import db

def run_migration():
    """Execute the notification preferences migration."""
    print("🔄 Running notification preferences migration...")
    
    with app.app_context():
        try:
            # Read SQL migration file
            migration_file = Path(__file__).parent / 'add_notification_preferences.sql'
            
            if not migration_file.exists():
                print("❌ Migration file not found!")
                return False
            
            sql_content = migration_file.read_text()
            
            # Remove comment lines first to avoid issues with statements preceded by comments
            lines = [line for line in sql_content.split('\n') if not line.strip().startswith('--')]
            clean_content = '\n'.join(lines)
            
            # Split into individual statements and execute
            statements = [s.strip() for s in clean_content.split(';') if s.strip()]
            
            for stmt in statements:
                if stmt:
                    try:
                        db.session.execute(db.text(stmt))
                        print(f"  ✓ Executed: {stmt[:60]}...")
                    except Exception as e:
                        # Ignore "column already exists" errors
                        if 'Duplicate column' in str(e) or 'already exists' in str(e):
                            print(f"  ⏭ Skipped (already exists): {stmt[:40]}...")
                        else:
                            raise e
            
            db.session.commit()
            print("✅ Migration completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    success = run_migration()
    sys.exit(0 if success else 1)
