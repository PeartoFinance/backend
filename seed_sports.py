from app import app, db
from models.media import SportsCategory

def seed_sports():
    """Seed default sports categories"""
    sports = [
        {
            'name': 'Football',
            'key': 'football',
            'api_url': 'https://v3.football.api-sports.io',
            'icon': 'Trophy',
            'is_active': True
        },
        {
            'name': 'Basketball',
            'key': 'basketball',
            'api_url': 'https://v1.basketball.api-sports.io',
            'icon': 'Dribbble',
            'is_active': True
        },
        {
            'name': 'Baseball',
            'key': 'baseball',
            'api_url': 'https://v1.baseball.api-sports.io',
            'icon': 'Baseball',
            'is_active': True
        },
        {
            'name': 'Rugby',
            'key': 'rugby',
            'api_url': 'https://v1.rugby.api-sports.io',
            'icon': 'Grab', 
            'is_active': False
        },
        {
            'name': 'Hockey',
            'key': 'hockey',
            'api_url': 'https://v1.hockey.api-sports.io',
            'icon': 'Disc',
            'is_active': False
        },
        # New Sports
        {
            'name': 'AFL',
            'key': 'afl',
            'api_url': 'https://v1.afl.api-sports.io',
            'icon': 'Activity',
            'is_active': False
        },
        {
            'name': 'Formula 1',
            'key': 'formula-1',
            'api_url': 'https://v1.formula-1.api-sports.io',
            'icon': 'Car',
            'is_active': False
        },
        {
            'name': 'Handball',
            'key': 'handball',
            'api_url': 'https://v1.handball.api-sports.io',
            'icon': 'Grab',
            'is_active': False
        },
        {
            'name': 'MMA',
            'key': 'mma',
            'api_url': 'https://v1.mma.api-sports.io',
            'icon': 'Swords',
            'is_active': False
        },
        {
            'name': 'NBA',
            'key': 'nba',
            'api_url': 'https://v2.nba.api-sports.io',
            'icon': 'Dribbble',
            'is_active': True
        },
        {
            'name': 'NFL',
            'key': 'nfl',
            'api_url': 'https://v1.american-football.api-sports.io',
            'icon': 'Shirt',
            'is_active': True
        },
        {
            'name': 'Volleyball',
            'key': 'volleyball',
            'api_url': 'https://v1.volleyball.api-sports.io',
            'icon': 'Volleyball',
            'is_active': False
        }
    ]

    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        
        print("Seeding sports categories...")
        for sport_data in sports:
            existing = SportsCategory.query.filter_by(key=sport_data['key']).first()
            if not existing:
                new_sport = SportsCategory(**sport_data)
                db.session.add(new_sport)
                print(f"Added {sport_data['name']}")
            else:
                # Update existing
                existing.name = sport_data['name']
                existing.api_url = sport_data['api_url']
                existing.icon = sport_data['icon']
                existing.is_active = sport_data['is_active']
                print(f"Updated {sport_data['name']}")
        
        db.session.commit()
        print("Done!")

if __name__ == '__main__':
    seed_sports()
