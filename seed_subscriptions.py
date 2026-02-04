from datetime import datetime
from flask import Flask
from config import config
from models.base import db
from models.subscription import SubscriptionPlan
from app import create_app

def seed_subscription_plans():
    """Create demo subscription plans with features and usage limits"""
    plans = [
        {
            'name': 'Free',
            'description': 'Essential tools for casual investors',
            'price': 0,
            'currency': 'USD',
            'interval': 'monthly', # Although free, it needs an interval context usually, or handle as special
            'duration_days': 30,
            'features': {
                # Boolean toggles
                'real_time_data': True,
                'advanced_charts': False,
                'ai_insights': False,
                'portfolio_tracking': True,
                'unlimited_alerts': False,
                'download_reports': False,
                'priority_support': False,
                # Usage limits (configurable by admin)
                'ai_queries_limit': 5,           # per day
                'advanced_charts_limit': 3,      # per day
                'download_reports_limit': 3,     # per month
                'alerts_limit': 3,               # total
                'chart_templates_limit': 1,      # total
            },
            'max_members': 1,
            'is_featured': False,
            'is_active': True
        },
        {
            'name': 'Pro',
            'description': 'Advanced analytics and AI insights for serious traders',
            'price': 19.99,
            'currency': 'USD',
            'interval': 'monthly',
            'duration_days': 30,
            'features': {
                # Boolean toggles
                'real_time_data': True,
                'advanced_charts': True,
                'ai_insights': True,
                'portfolio_tracking': True,
                'unlimited_alerts': True,
                'download_reports': True,
                'priority_support': False,
                # Usage limits (-1 = unlimited)
                'ai_queries_limit': -1,
                'advanced_charts_limit': -1,
                'download_reports_limit': -1,
                'alerts_limit': -1,
                'chart_templates_limit': -1,
            },
            'max_members': 1,
            'is_featured': True,
            'is_active': True
        },
        {
            'name': 'Pro Yearly',
            'description': 'Best value for long-term investors',
            'price': 199.99,
            'currency': 'USD',
            'interval': 'yearly',
            'duration_days': 365,
            'features': {
                # Boolean toggles
                'real_time_data': True,
                'advanced_charts': True,
                'ai_insights': True,
                'portfolio_tracking': True,
                'unlimited_alerts': True,
                'download_reports': True,
                'priority_support': True,
                # Usage limits (-1 = unlimited)
                'ai_queries_limit': -1,
                'advanced_charts_limit': -1,
                'download_reports_limit': -1,
                'alerts_limit': -1,
                'chart_templates_limit': -1,
            },
            'max_members': 1,
            'is_featured': False,
            'is_active': True
        }
    ]

    # Clear existing plans if requested (for fresh start)
    clear_first = True  # Set to True to remove all old plans first
    
    if clear_first:
        old_plans = SubscriptionPlan.query.all()
        for old_plan in old_plans:
            db.session.delete(old_plan)
        db.session.commit()
        print(f"Cleared {len(old_plans)} existing plans")

    count = 0
    for p in plans:
        existing = SubscriptionPlan.query.filter_by(name=p['name']).first()
        if existing:
            # Update existing plan with new data
            existing.description = p['description']
            existing.price = p['price']
            existing.currency = p['currency']
            existing.interval = p['interval']
            existing.duration_days = p['duration_days']
            existing.features = p['features']
            existing.max_members = p['max_members']
            existing.is_featured = p['is_featured']
            existing.is_active = p['is_active']
            print(f"Updated plan: {p['name']}")
        else:
            plan = SubscriptionPlan(
                name=p['name'],
                description=p['description'],
                price=p['price'],
                currency=p['currency'],
                interval=p['interval'],
                duration_days=p['duration_days'],
                features=p['features'],
                max_members=p['max_members'],
                is_featured=p['is_featured'],
                is_active=p['is_active']
            )
            db.session.add(plan)
            count += 1
            print(f"Added plan: {p['name']}")

    db.session.commit()
    print(f"✓ Seeded {count} new subscription plans")

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        seed_subscription_plans()
