from app import app
from models import db, NewsItem

def publish_all_drafts():
    with app.app_context():
        print("Checking for draft news items...")
        drafts = NewsItem.query.filter_by(curated_status='draft').all()
        count = len(drafts)
        
        if count == 0:
            print("No draft items found.")
            return

        print(f"Found {count} draft items. Updating to 'published'...")
        
        for item in drafts:
            item.curated_status = 'published'
            
        try:
            db.session.commit()
            print(f"Successfully published {count} items.")
        except Exception as e:
            db.session.rollback()
            print(f"Error updating items: {e}")

if __name__ == "__main__":
    publish_all_drafts()
