"""
Quick script to mark Phase 1-3 tools as implemented
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models.base import db
from models.settings import ToolSettings

# All implemented tools (Phase 1-3)
IMPLEMENTED_SLUGS = [
    # Writing tools
    'word-counter',
    'case-converter',
    'lorem-ipsum',
    'reading-time',
    
    # Code tools
    'json-formatter',
    'csv-to-json',
    'user-agent-parser',
    
    # Design tools
    'color-palette',
    'gradient-generator',
    'qr-code-generator',
    
    # Fun tools
    'love-calculator',
    'random-number',
    
    # Additional utilities
    'decision-maker',
    
    # Productivity
    'pomodoro-timer',
    'meeting-cost-calculator',
    
    # Marketing
    'hashtag-generator',
    'cpc-calculator',
    'roas-calculator',
    
    # SEO
    'meta-tag-generator',
    
    # E-commerce
    'profit-margin',
    'discount-calculator',
    
    # Education
    'gpa-calculator',
    'study-planner',
    
    # Cooking
    'recipe-scaler',
    
    # Travel
    'trip-cost',
    'vacation-budget',
    
    # Real Estate
    'square-footage',
    'down-payment',
    
    # Health
    'target-heart-rate',
    'medication-dosage',
    'ovulation-calculator',
    
    # Gaming
    'game-stats',
    
    # Legal
    'contract-value',
    
    # Insurance
    'insurance-premium',
    
    # Portfolio
    'asset-allocation',
]

def update_implemented():
    app = create_app()
    with app.app_context():
        updated = 0
        for slug in IMPLEMENTED_SLUGS:
            tool = ToolSettings.query.filter_by(tool_slug=slug).first()
            if tool and not tool.is_implemented:
                tool.is_implemented = True
                updated += 1
                print(f"  ✓ Marked as implemented: {slug}")
            elif not tool:
                print(f"  ✗ Not found in database: {slug}")
        
        db.session.commit()
        print(f"\nUpdated {updated} tools to implemented status")

if __name__ == '__main__':
    update_implemented()
