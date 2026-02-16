from app import app
from models import db, NewsItem
from sqlalchemy import func

def check_counts():
    with app.app_context():
        print("--- News Item Counts ---")
        total = NewsItem.query.count()
        print(f"Total Items: {total}")
        
        print("\n--- By Status ---")
        by_status = db.session.query(NewsItem.curated_status, func.count(NewsItem.id)).group_by(NewsItem.curated_status).all()
        for status, count in by_status:
            print(f"{status}: {count}")
            
        print("\n--- By Country ---")
        by_country = db.session.query(NewsItem.country_code, func.count(NewsItem.id)).group_by(NewsItem.country_code).all()
        for country, count in by_country:
            print(f"{country}: {count}")

if __name__ == "__main__":
    check_counts()
