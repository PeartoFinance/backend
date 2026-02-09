
import yfinance as yf
import pandas as pd
import logging
import sys
import os

# Add backend to path
sys.path.append(os.getcwd())

from handlers.market_data import get_yfinance_session

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MAJOR_INDICES = {
    # US Indices
    '^GSPC': 'S&P 500',
    # ... (rest same)
    '^DJI': 'Dow Jones Industrial Average',
    '^IXIC': 'NASDAQ Composite',
    '^RUT': 'Russell 2000',
    '^VIX': 'CBOE Volatility Index',
    '^NYA': 'NYSE Composite',
    '^NDX': 'NASDAQ 100',
    # European Indices
    '^FTSE': 'FTSE 100',
    '^GDAXI': 'DAX',
    '^FCHI': 'CAC 40',
    '^STOXX50E': 'EURO STOXX 50',
    '^IBEX': 'IBEX 35',
    # Asian Indices
    '^N225': 'Nikkei 225',
    '^HSI': 'Hang Seng',
    '000001.SS': 'Shanghai Composite',
    '^KS11': 'KOSPI',
    '^TWII': 'Taiwan Weighted',
    '^BSESN': 'BSE SENSEX',
    '^NSEI': 'NIFTY 50',
    # Other
    '^GSPTSE': 'S&P/TSX Composite',
    '^AXJO': 'S&P/ASX 200',
}

def test_download():
    symbols = list(MAJOR_INDICES.keys())
    print(f"Testing download for {len(symbols)} symbols: {symbols}")
    
    session = get_yfinance_session()
    print(f"Using session: {session} (curl_cffi={getattr(session, '_is_curl_cffi', 'Unknown')})")
    
    try:
        data = yf.download(
            symbols,
            period='2d',
            interval='1d',
            group_by='ticker',
            progress=True,
            session=session,
            threads=False
        )
        
        print(f"\nDownload complete. Shape: {data.shape}")
        if data.empty:
            print("❌ Data is empty!")
            return

        print("\nColumns:")
        print(data.columns)
        
        print("\nFirst few rows:")
        print(data.head())
        
        # Check individual symbols
        print("\nChecking individual symbols:")
        success_count = 0
        for symbol in symbols:
            try:
                if symbol in data.columns.get_level_values(0):
                    print(f"✅ {symbol}: Found")
                    success_count += 1
                else:
                    print(f"❌ {symbol}: NOT FOUND in columns")
            except Exception as e:
                print(f"⚠️ {symbol}: Error checking - {e}")
                
        print(f"\nSuccess rate: {success_count}/{len(symbols)}")

    except Exception as e:
        print(f"❌ Exception during download: {e}")

if __name__ == "__main__":
    test_download()
