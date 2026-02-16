"""
One-time migration: publish all draft news and assign categories to existing items.
Run via: python3 migrate_news_data.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import app
from models import db, NewsItem
from services.news_source_manager import detect_category

with app.app_context():
    # 1. Publish all drafts
    draft_count = NewsItem.query.filter_by(curated_status='draft').update(
        {'curated_status': 'published'}, synchronize_session=False
    )
    db.session.commit()
    print(f"[1/2] Published {draft_count} draft news items")

    # 2. Assign categories to items with NULL category
    uncategorized = NewsItem.query.filter(
        (NewsItem.category == None) | (NewsItem.category == '')
    ).all()
    print(f"[2/2] Found {len(uncategorized)} uncategorized items, assigning categories...")

    updated = 0
    for item in uncategorized:
        cat = detect_category(item.title or '', item.summary or '')
        item.category = cat
        updated += 1

    db.session.commit()
    print(f"       Updated {updated} items with auto-detected categories")

    # Summary
    from sqlalchemy import func
    rows = db.session.query(
        NewsItem.category, func.count(NewsItem.id)
    ).group_by(NewsItem.category).order_by(func.count(NewsItem.id).desc()).all()
    
    print("\n=== Category Distribution ===")
    for cat, count in rows:
        print(f"  {cat or 'NULL'}: {count}")
    
    total = NewsItem.query.filter_by(curated_status='published').count()
    print(f"\nTotal published news items: {total}")
