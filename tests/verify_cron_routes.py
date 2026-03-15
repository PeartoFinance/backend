import requests
import time

BASE_URL = "https://apipearto.ashlya.com/api/cron"
TOKEN = "123456789"
HEADERS = {'X-Cron-Token': TOKEN}

endpoints = [
    '/stocks',
    '/crypto',
    '/indices',
    '/commodities',
    '/earnings',
    '/dividends',
    '/watchlist-alerts',
    '/earnings-alerts',
    '/portfolio-summary',
    '/daily-digest',
    '/all-market',
    '/business-profiles',
    '/cleanup-accounts',
    '/cleanup-news',
    '/financials',
    '/forecast',
    '/import-news',
    '/import-stock-profiles',
    '/import-business-profiles',
    '/news-notifications',
    '/forex',
    '/wealth-snapshot',
    '/check-goals'
]

print(f"Verifying {len(endpoints)} endpoints...")

results = []

for endpoint in endpoints:
    url = f"{BASE_URL}{endpoint}?token={TOKEN}"
    print(f"Testing {endpoint}...", end=" ", flush=True)
    try:
        start_time = time.time()
        # Using GET as per user request examples
        response = requests.get(url, timeout=300) 
        duration = time.time() - start_time
        
        status = "OK" if response.status_code == 200 else f"FAIL ({response.status_code})"
        print(f"{status} - {duration:.2f}s")
        
        results.append({
            'endpoint': endpoint,
            'status': response.status_code,
            'response': response.text[:200], # First 200 chars
            'duration': duration
        })
        
        if response.status_code != 200:
            print(f"  Error: {response.text}")

    except Exception as e:
        print(f"ERROR: {e}")
        results.append({
            'endpoint': endpoint,
            'status': 'EXCEPTION',
            'response': str(e),
            'duration': 0
        })

print("\n--- Summary ---")
failed = [r for r in results if r['status'] != 200]
if not failed:
    print("All tested endpoints passed!")
else:
    print(f"{len(failed)} endpoints failed:")
    for f in failed:
        print(f"  {f['endpoint']}: {f['status']} - {f['response']}")
