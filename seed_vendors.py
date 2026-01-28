"""
Seed Vendors Script
Populates the database with demo vendor data for testing.
"""
import uuid
from datetime import datetime
from app import create_app
from models import db, Vendor, VendorReview, VendorHistory, NavigationItem
from datetime import datetime, timedelta
import random

app = create_app()

def seed_vendors():
    with app.app_context():
        print("Seeding vendors, reviews, history, and navigation...")
        
        # Clear existing demo vendors (optional, but good for idempotency if we had a way to identify them)
        # For now, we'll just add them.
        
        vendors_data = [
            # Real Estate / Mortgage
            {
                "name": "QuickHome Loans",
                "category": "Real Estate",
                "services": ["Mortgage", "Refinancing", "Home Equity"],
                "rating": 4.8,
                "review_count": 1240,
                "is_featured": True,
                "description": "Fast and easy digital mortgage application process with competitive rates.",
                "website": "https://example.com/quickhome",
                "logo_url": "https://ui-avatars.com/api/?name=OH&background=0D9488&color=fff"
            },
            {
                "name": "TrustBank Mortgages",
                "category": "Real Estate",
                "services": ["Home Loans", "Construction Loans"],
                "rating": 4.5,
                "review_count": 850,
                "is_featured": False,
                "description": "Traditional banking reliability with modern loan options.",
                "website": "https://example.com/trustbank",
                "logo_url": "https://ui-avatars.com/api/?name=TB&background=2563EB&color=fff"
            },
            
            # Banking / Loans (FD, RD, Personal Loans)
            {
                "name": "SecureSave Bank",
                "category": "Banking",
                "services": ["Fixed Deposits", "Personal Loans", "Savings"],
                "rating": 4.7,
                "review_count": 3200,
                "is_featured": True,
                "description": "High interest rates on Fixed Deposits and minimal fees on loans.",
                "website": "https://example.com/securesave",
                "logo_url": "https://ui-avatars.com/api/?name=SS&background=7C3AED&color=fff"
            },
            {
                "name": "Global FinCorp",
                "category": "Banking",
                "services": ["Business Loans", "Recurring Deposits"],
                "rating": 4.3,
                "review_count": 560,
                "is_featured": False,
                "description": "Global banking solutions for your personal and business needs.",
                "website": "https://example.com/globalfin",
                "logo_url": "https://ui-avatars.com/api/?name=GF&background=DB2777&color=fff"
            },

            # Investment (SIP, Mutual Funds, Stocks)
            {
                "name": "GrowWealth",
                "category": "Investment",
                "services": ["Mutual Funds", "SIP", "Stocks"],
                "rating": 4.9,
                "review_count": 5400,
                "is_featured": True,
                "description": "Zero commission mutual fund investments and simplified SIPs.",
                "website": "https://example.com/growwealth",
                "logo_url": "https://ui-avatars.com/api/?name=GW&background=059669&color=fff"
            },
            {
                "name": "Alpha Traders",
                "category": "Investment",
                "services": ["Stocks", "F&O", "Commodities"],
                "rating": 4.6,
                "review_count": 1200,
                "is_featured": False,
                "description": "Advanced trading platforms for active investors.",
                "website": "https://example.com/alpha",
                "logo_url": "https://ui-avatars.com/api/?name=AT&background=D97706&color=fff"
            },

            # Insurance
            {
                "name": "LifeGuard Insurance",
                "category": "Insurance",
                "services": ["Term Life", "Health Insurance"],
                "rating": 4.8,
                "review_count": 2100,
                "is_featured": True,
                "description": "Comprehensive life and health coverage for your family.",
                "website": "https://example.com/lifeguard",
                "logo_url": "https://ui-avatars.com/api/?name=LG&background=DC2626&color=fff"
            },

            # Tax / Government Schemes (PPF, NPS)
            {
                "name": "TaxSaver Pro",
                "category": "Tax Services",
                "services": ["Tax Filing", "NPS Advisory", "PPF Consultation"],
                "rating": 4.4,
                "review_count": 890,
                "is_featured": False,
                "description": "Expert assistance for tax saving investments and filing.",
                "website": "https://example.com/taxsaver",
                "logo_url": "https://ui-avatars.com/api/?name=TS&background=475569&color=fff"
            }
        ]

        for data in vendors_data:
            # Check if exists by name to avoid dupes in this simple script
            if Vendor.query.filter_by(name=data['name']).first():
                print(f"Skipping {data['name']} (already exists)")
                continue

            vendor = Vendor(
                id=str(uuid.uuid4()),
                name=data['name'],
                category=data['category'],
                services=data['services'],
                rating=data['rating'],
                review_count=data['review_count'],
                is_featured=data['is_featured'],
                description=data['description'],
                website=data['website'],
                logo_url=data['logo_url'],
                status='active',
                country_code='US',
                created_at=datetime.utcnow()
            )
            db.session.add(vendor)
            print(f"Added {data['name']}")
        
        db.session.commit()

        # Seed Reviews and History
        vendors = Vendor.query.all()
        for v in vendors:
            # Reviews
            if not v.reviews:
                print(f"Adding reviews for {v.name}")
                for _ in range(random.randint(3, 10)):
                    review = VendorReview(
                        id=str(uuid.uuid4()),
                        vendor_id=v.id,
                        user_id=1, # Assuming user ID 1 exists (admin/demo user)
                        rating=random.randint(3, 5),
                        comment=random.choice([
                            "Great service, highly recommended!",
                            "Process was smooth and fast.",
                            "Customer support was very helpful.",
                            "Rates are competitive.",
                            "A bit slow but got the job done.",
                            "Trustworthy and reliable."
                        ]),
                        is_verified_customer=random.choice([True, False]),
                        created_at=datetime.utcnow() - timedelta(days=random.randint(1, 100))
                    )
                    db.session.add(review)

            # History - Interest Rates or Stock Value
            if not v.history:
                print(f"Adding history for {v.name}")
                metric_type = 'interest_rate' if v.category in ['Banking', 'Real Estate', 'Investment'] else 'customer_satisfaction'
                base_val = float(v.rating) * 2 if metric_type == 'customer_satisfaction' else random.uniform(5.0, 12.0)
                
                for i in range(12): # Last 12 months
                    val = base_val + random.uniform(-0.5, 0.5)
                    hist = VendorHistory(
                        vendor_id=v.id,
                        metric_type=metric_type,
                        value=round(val, 2),
                        recorded_at=datetime.utcnow() - timedelta(days=30 * (12 - i))
                    )
                    db.session.add(hist)

        db.session.commit()
        
        # Seed Navigation
        print("Ensuring Partners navigation item exists...")
        existing_nav = NavigationItem.query.filter_by(url='/vendors').first()
        if not existing_nav:
            partners_nav = NavigationItem(
                label='Partners',
                url='/vendors',
                icon='Briefcase',
                section='sidebar_main',
                order_index=50,
                is_active=True,
                requires_auth=False
            )
            db.session.add(partners_nav)
            db.session.commit()
            print("Added Partners navigation item.")
        else:
            print("Partners navigation item already exists.")

        print("Done!")

if __name__ == '__main__':
    seed_vendors()
