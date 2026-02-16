import sys
import os
import logging

# Add current directory to path so we can import handlers
sys.path.append(os.getcwd())

import yfinance as yf
from handlers.market_data import get_yfinance_session

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_yfinance")

def test_session():
    print("Testing YFinance with curl_cffi session...")
    
    session = get_yfinance_session()
    print(f"Session created: {type(session)}")
    
    symbol = "AAPL"
    
    # Test 1: ticker.info (Scraping)
    print(f"\n1. Testing yf.Ticker('{symbol}').info ...")
    try:
        ticker = yf.Ticker(symbol, session=session)
        info = ticker.info
        if info and 'symbol' in info:
            print(f"✅ SUCCESS: Got info for {info['symbol']}")
        else:
            print("❌ FAILURE: Info empty or missing symbol")
    except Exception as e:
        print(f"❌ ERROR: {e}")

    # Test 2: ticker.history (API)
    print(f"\n2. Testing yf.Ticker('{symbol}').history ...")
    try:
        ticker = yf.Ticker(symbol, session=session)
        hist = ticker.history(period="1d", interval="1m")
        if not hist.empty:
            print(f"✅ SUCCESS: Got {len(hist)} rows of history")
        else:
            print("❌ FAILURE: History empty")
    except Exception as e:
        print(f"❌ ERROR: {e}")

    # Test 3: yf.download (Bulk API)
    print(f"\n3. Testing yf.download(['{symbol}']) ...")
    try:
        data = yf.download([symbol], period="1d", interval="1m", session=session, progress=False, threads=False)
        if not data.empty:
            print(f"✅ SUCCESS: Got download data")
        else:
            print("❌ FAILURE: Download data empty")
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    test_session()
