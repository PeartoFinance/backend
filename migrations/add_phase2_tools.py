"""
Script to add new Phase 2-3 tools to database and mark as implemented
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models.base import db
from models.settings import ToolSettings

# New tools to add (Phase 2-3)
NEW_TOOLS = [
    # Fun
    {'tool_slug': 'random-number', 'tool_name': 'Random Number Generator', 'category': 'Fun & Entertainment'},
    
    # Marketing
    {'tool_slug': 'roas-calculator', 'tool_name': 'ROAS Calculator', 'category': 'Marketing'},
    
    # E-commerce
    {'tool_slug': 'discount-calculator', 'tool_name': 'Discount Calculator', 'category': 'E-commerce'},
    
    # Education
    {'tool_slug': 'study-planner', 'tool_name': 'Study Planner', 'category': 'Education & Study'},
    
    # Travel
    {'tool_slug': 'vacation-budget', 'tool_name': 'Vacation Budget Planner', 'category': 'Travel'},
    
    # Real Estate
    {'tool_slug': 'down-payment', 'tool_name': 'Down Payment Calculator', 'category': 'Real Estate'},
    
    # Health
    {'tool_slug': 'medication-dosage', 'tool_name': 'Medication Dosage Calculator', 'category': 'Health & Medical'},
    {'tool_slug': 'ovulation-calculator', 'tool_name': 'Ovulation Calculator', 'category': 'Health & Medical'},
    
    # Gaming
    {'tool_slug': 'game-stats', 'tool_name': 'Game Stats Calculator', 'category': 'Gaming'},
    
    # Legal
    {'tool_slug': 'contract-value', 'tool_name': 'Contract Value Calculator', 'category': 'Legal'},
    
    # Insurance
    {'tool_slug': 'insurance-premium', 'tool_name': 'Insurance Premium Estimator', 'category': 'Insurance'},
    
    # Portfolio
    {'tool_slug': 'asset-allocation', 'tool_name': 'Asset Allocation Calculator', 'category': 'Portfolio Analysis'},
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
