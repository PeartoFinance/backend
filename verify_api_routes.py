import requests
import json
import time

BASE_URL = "http://localhost:5000"

ENDPOINTS = [
    {"name": "Health Check", "url": "/api/health", "method": "GET"},
    {"name": "Market Indices", "url": "/api/market/indices", "method": "GET"},
    {"name": "Market Overview", "url": "/api/market/overview", "method": "GET"},
    {"name": "Stock Search (AAPL)", "url": "/api/stocks/search?q=AAPL", "method": "GET"},
    {"name": "Stock Profile (AAPL)", "url": "/api/stocks/profile/AAPL", "method": "GET"},
    {"name": "Stock History (AAPL 1d 1m)", "url": "/api/stocks/history/AAPL?period=1d&interval=1m", "method": "GET"},
    {"name": "Crypto Markets", "url": "/api/crypto/markets", "method": "GET"},
    {"name": "Crypto Details (BTC-USD)", "url": "/api/crypto/coin/BTC-USD", "method": "GET"},
    {"name": "Crypto History (BTC-USD 1d 1m)", "url": "/api/crypto/history/BTC-USD?period=1d&interval=1m", "method": "GET"},
]

def run_tests():
    print(f"Starting API Verification on {BASE_URL}...\n")
    results = []
    
    for endpoint in ENDPOINTS:
        name = endpoint["name"]
        url = BASE_URL + endpoint["url"]
        print(f"Testing {name}...", end=" ", flush=True)
        
        try:
            start_time = time.time()
            response = requests.get(url, timeout=10)
            elapsed = time.time() - start_time
            
            status = response.status_code
            try:
                data = response.json()
                data_preview = str(data)[:100] + "..." if len(str(data)) > 100 else str(data)
            except:
                data = response.text
                data_preview = data[:100] + "..."
            
            if status == 200:
                print(f"✅ OK ({status}) - {elapsed:.2f}s")
                results.append({"name": name, "status": "PASS", "code": status, "time": elapsed})
            else:
                print(f"❌ FAILED ({status}) - {elapsed:.2f}s")
                print(f"   Response: {data_preview}")
                results.append({"name": name, "status": "FAIL", "code": status, "time": elapsed, "error": data_preview})
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            results.append({"name": name, "status": "ERROR", "error": str(e)})
            
    print("\n" + "="*40)
    print("SUMMARY")
    print("="*40)
    passed = sum(1 for r in results if r["status"] == "PASS")
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed < total:
        print("\nFailures:")
        for r in results:
            if r["status"] != "PASS":
                print(f"- {r['name']}: {r.get('code', 'N/A')} - {r.get('error', '')}")

if __name__ == "__main__":
    run_tests()
