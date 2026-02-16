#!/usr/bin/env python3
"""
API Performance and Rate Limit Tester
Tests PeartoFinance API endpoints for response time, caching, and rate limiting
"""
import requests
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import json

# Configuration
BASE_URL = "http://api.pearto.com/api"

# Endpoints to test
ENDPOINTS = [
    # Live endpoints (cached 300s)
    "/live/dashboard",
    "/live/indices",
    "/live/commodities",
    "/live/forex",
    "/live/crypto",
    "/live/stocks",
    "/live/movers",
    "/live/most-active",
    # Market endpoints (cached 300s)
    "/market/overview",
    "/market/indices",
    "/market/forex",
    "/market/commodities",
    # Stocks endpoints
    "/stocks/movers",
    "/stocks/most-active",
    "/stocks/sectors",
]

def test_single_request(endpoint, timeout=30):
    """Test a single API request and return response time and status"""
    url = f"{BASE_URL}{endpoint}"
    start = time.time()
    try:
        response = requests.get(url, timeout=timeout)
        elapsed = (time.time() - start) * 1000  # Convert to ms
        
        # Check response content
        try:
            data = response.json()
            data_count = len(data) if isinstance(data, list) else len(data.keys()) if isinstance(data, dict) else 0
        except:
            data_count = 0
            
        return {
            "endpoint": endpoint,
            "status": response.status_code,
            "time_ms": round(elapsed, 2),
            "data_count": data_count,
            "success": response.status_code == 200 and data_count > 0
        }
    except requests.exceptions.Timeout:
        return {"endpoint": endpoint, "status": "TIMEOUT", "time_ms": timeout * 1000, "success": False}
    except requests.exceptions.RequestException as e:
        return {"endpoint": endpoint, "status": "ERROR", "time_ms": 0, "error": str(e), "success": False}

def test_rapid_requests(endpoint, count=10, delay=0.1):
    """Test rapid requests to check caching effectiveness"""
    print(f"\n🔄 Testing {count} rapid requests to {endpoint}...")
    results = []
    
    for i in range(count):
        result = test_single_request(endpoint)
        results.append(result)
        print(f"  Request {i+1}: {result['status']} - {result['time_ms']}ms - Items: {result.get('data_count', 0)}")
        time.sleep(delay)
    
    # Calculate stats
    times = [r['time_ms'] for r in results if r['status'] == 200]
    if times:
        print(f"\n  📊 Stats for {endpoint}:")
        print(f"     Min: {min(times):.0f}ms | Max: {max(times):.0f}ms | Avg: {statistics.mean(times):.0f}ms")
        if len(times) > 1:
            print(f"     StdDev: {statistics.stdev(times):.0f}ms")
        
        # Check if caching is effective (subsequent requests should be faster)
        if len(times) >= 3 and times[0] > times[2] * 2:
            print(f"     ✅ Caching appears effective (first request slower)")
    
    return results

def test_concurrent_requests(endpoints, max_workers=5):
    """Test multiple endpoints concurrently"""
    print(f"\n⚡ Testing {len(endpoints)} endpoints concurrently...")
    results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(test_single_request, ep): ep for ep in endpoints}
        for future in as_completed(futures):
            result = future.result()
            status_icon = "✅" if result['success'] else "❌"
            print(f"  {status_icon} {result['endpoint']}: {result['status']} - {result['time_ms']}ms")
            results.append(result)
    
    return results

def test_all_endpoints():
    """Test all endpoints once"""
    print("\n📋 Testing all endpoints once...")
    results = []
    
    for endpoint in ENDPOINTS:
        result = test_single_request(endpoint)
        status_icon = "✅" if result['success'] else "❌" if result['status'] != 200 else "⚠️"
        print(f"  {status_icon} {endpoint}: {result['status']} - {result['time_ms']:.0f}ms - Items: {result.get('data_count', 0)}")
        results.append(result)
    
    return results

def print_summary(results):
    """Print test summary"""
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"Total requests: {len(results)}")
    print(f"✅ Successful: {len(successful)}")
    print(f"❌ Failed: {len(failed)}")
    
    if successful:
        times = [r['time_ms'] for r in successful]
        print(f"\n⏱️ Response Times (successful requests):")
        print(f"   Min: {min(times):.0f}ms")
        print(f"   Max: {max(times):.0f}ms")
        print(f"   Avg: {statistics.mean(times):.0f}ms")
    
    if failed:
        print(f"\n❌ Failed endpoints:")
        for r in failed:
            print(f"   • {r['endpoint']}: {r['status']}")

def main():
    print("="*60)
    print("🚀 PEARTO FINANCE API PERFORMANCE TESTER")
    print(f"   Base URL: {BASE_URL}")
    print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    all_results = []
    
    # Test 1: All endpoints once
    results = test_all_endpoints()
    all_results.extend(results)
    
    # Test 2: Rapid requests to test caching
    rapid_results = test_rapid_requests("/live/commodities", count=5, delay=0.2)
    all_results.extend(rapid_results)
    
    # Test 3: Concurrent requests
    concurrent_results = test_concurrent_requests(ENDPOINTS[:6], max_workers=3)
    all_results.extend(concurrent_results)
    
    # Print summary
    print_summary(all_results)
    
    print("\n✨ Testing complete!")

if __name__ == "__main__":
    main()
