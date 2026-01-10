#!/usr/bin/env python3
"""
Test script for yfinance market data handlers
"""
import sys
sys.path.insert(0, '/home/bishal-regmi/Desktop/PeartoFinance/backend')

print("=" * 60)
print("YFinance Market Data Handler Tests")
print("=" * 60)

# Test 1: Stock Quote
print("\n[TEST 1] Stock Quote - AAPL")
from handlers.market_data.stock_handler import get_stock_quote
quote = get_stock_quote('AAPL')
if quote:
    print(f"  ✓ Symbol: {quote.get('symbol')}")
    print(f"  ✓ Name: {quote.get('name')}")
    print(f"  ✓ Price: ${quote.get('price')}")
    print(f"  ✓ Change: {quote.get('changePercent')}%")
    print(f"  ✓ Sector: {quote.get('sector')}")
else:
    print("  ✗ Failed to get quote")

# Test 2: Multiple Stock Quotes
print("\n[TEST 2] Multiple Stock Quotes - MSFT, GOOGL")
from handlers.market_data.stock_handler import get_multiple_quotes
quotes = get_multiple_quotes(['MSFT', 'GOOGL'])
print(f"  ✓ Got {len(quotes)} quotes")
for q in quotes:
    print(f"    - {q.get('symbol')}: ${q.get('price')}")

# Test 3: Crypto Quote
print("\n[TEST 3] Crypto Quote - BTC-USD")
from handlers.market_data.crypto_handler import get_crypto_quote
crypto = get_crypto_quote('BTC')
if crypto:
    print(f"  ✓ Symbol: {crypto.get('symbol')}")
    print(f"  ✓ Name: {crypto.get('name')}")
    print(f"  ✓ Price: ${crypto.get('price')}")
else:
    print("  ✗ Failed to get crypto quote")

# Test 4: Market Index
print("\n[TEST 4] Index Quote - S&P 500")
from handlers.market_data.index_handler import get_index_quote
index = get_index_quote('^GSPC')
if index:
    print(f"  ✓ Symbol: {index.get('symbol')}")
    print(f"  ✓ Name: {index.get('name')}")
    print(f"  ✓ Price: {index.get('price')}")
else:
    print("  ✗ Failed to get index quote")

# Test 5: Commodity
print("\n[TEST 5] Commodity Quote - Gold")
from handlers.market_data.commodity_handler import get_commodity_quote
commodity = get_commodity_quote('GC=F')
if commodity:
    print(f"  ✓ Symbol: {commodity.get('symbol')}")
    print(f"  ✓ Name: {commodity.get('name')}")
    print(f"  ✓ Price: ${commodity.get('price')}/oz")
else:
    print("  ✗ Failed to get commodity quote")

# Test 6: Stock History
print("\n[TEST 6] Stock History - AAPL (1 week)")
from handlers.market_data.stock_handler import get_stock_history
history = get_stock_history('AAPL', period='5d')
print(f"  ✓ Got {len(history)} data points")
if history:
    print(f"    Latest: {history[-1].get('date')} - Close: ${history[-1].get('close'):.2f}")

# Test 7: Search
print("\n[TEST 7] Search - 'apple'")
from handlers.market_data.search_handler import search_tickers
results = search_tickers('apple', max_results=5)
print(f"  ✓ Found {len(results.get('quotes', []))} matches")
for q in results.get('quotes', [])[:3]:
    print(f"    - {q.get('symbol')}: {q.get('name')}")

# Test 8: Day Gainers
print("\n[TEST 8] Screener - Day Gainers")
from handlers.market_data.screener_handler import get_day_gainers
gainers = get_day_gainers(limit=5)
print(f"  ✓ Found {len(gainers)} gainers")
for g in gainers[:3]:
    print(f"    - {g.get('symbol')}: +{g.get('changePercent'):.2f}%")

print("\n" + "=" * 60)
print("All tests completed!")
print("=" * 60)
