from app import app
from services.api_sports_service import APISportsService
from models.media import SportsCategory
import json

def debug_fetch():
    with app.app_context():
        print("--- Checking Active Sports ---")
        active = SportsCategory.query.filter_by(is_active=True).all()
        for s in active:
            print(f"- {s.name}: {s.api_url}")
            
        print("\n--- Fetching Fixtures (Live/All) ---")
        # Force fetch live first or all
        events = APISportsService.get_fixtures(status='all', date='2026-02-13')
        
        print(f"\nTotal Events Fetched: {len(events)}")
        
        sport_counts = {}
        for e in events:
            st = e.get('sportType', 'Unknown')
            sport_counts[st] = sport_counts.get(st, 0) + 1
            
        print("\n--- Event Distribution ---")
        for sport, count in sport_counts.items():
            print(f"{sport}: {count}")

        if not events:
            print("\nWARNING: No events returned. Testing individual API connection for Basketball...")
            # Try specific request
            import requests
            s = next((x for x in active if x.key == 'basketball'), None)
            if s:
                headers = APISportsService._get_headers(s.api_url)
                print(f"Requesting {s.api_url}/status with headers: {headers}")
                try:
                    r = requests.get(f"{s.api_url}/status", headers=headers)
                    print(f"Status Code: {r.status_code}")
                    print(f"Response: {r.text[:200]}...")
                except Exception as e:
                    print(f"Request failed: {e}")

if __name__ == "__main__":
    debug_fetch()
