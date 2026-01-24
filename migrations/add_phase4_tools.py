"""
Migration script to mark Phase 4 tools (with charts) as implemented
Uses Flask app context to connect to database
"""
import sys
import os

# Add parent directory to path to import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models.settings import ToolSettings

# Phase 4 tools - Advanced tools with charts
PHASE4_TOOLS = [
    'beta-calculator',
    'capital-gains-tax',
    'volatility-calculator',
    'market-crash-simulator',
    'travel-insurance',
    'college-savings',
]

def run_migration():
    with app.app_context():
        updated = 0
        
        for slug in PHASE4_TOOLS:
            tool = ToolSettings.query.filter_by(tool_slug=slug).first()
            
            if tool:
                if not tool.is_implemented:
                    tool.is_implemented = True
                    updated += 1
                    print(f"✓ Updated: {slug}")
                else:
                    print(f"○ Already implemented: {slug}")
            else:
                print(f"✗ Not found in DB: {slug}")
        
        db.session.commit()
        print(f"\nPhase 4 Migration Complete: {updated} tools updated")

if __name__ == '__main__':
    run_migration()
