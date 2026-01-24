"""
Script to add Phase 3 tools to database and mark as implemented
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models.base import db
from models.settings import ToolSettings

# New tools to add (Phase 3)
NEW_TOOLS = [
    # SEO
    {'tool_slug': 'keyword-density', 'tool_name': 'Keyword Density Checker', 'category': 'SEO'},
    
    # Cooking
    {'tool_slug': 'cooking-temp', 'tool_name': 'Cooking Temperature Guide', 'category': 'Cooking & Recipes'},
]

def add_and_mark_implemented():
    app = create_app()
    with app.app_context():
        added = 0
        for tool_data in NEW_TOOLS:
            existing = ToolSettings.query.filter_by(tool_slug=tool_data['tool_slug']).first()
            if not existing:
                new_tool = ToolSettings(
                    tool_slug=tool_data['tool_slug'],
                    tool_name=tool_data['tool_name'],
                    category=tool_data['category'],
                    enabled=True,
                    is_implemented=True,
                    order_index=100,
                    country_code='GLOBAL'
                )
                db.session.add(new_tool)
                added += 1
                print(f"  ✓ Added and marked as implemented: {tool_data['tool_slug']}")
            else:
                if not existing.is_implemented:
                    existing.is_implemented = True
                    print(f"  ✓ Updated to implemented: {tool_data['tool_slug']}")
                else:
                    print(f"  - Already exists: {tool_data['tool_slug']}")
        
        db.session.commit()
        print(f"\nAdded {added} new tools to database")

if __name__ == '__main__':
    add_and_mark_implemented()
