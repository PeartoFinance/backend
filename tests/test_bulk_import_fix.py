import sys
import os
import pandas as pd
import unittest
from unittest.mock import MagicMock, patch

# Add current directory to path
sys.path.append(os.getcwd())

from handlers.market_data import stock_handlers

class TestBulkImport(unittest.TestCase):
    @patch('yfinance.download')
    @patch('handlers.market_data.stock_handlers.get_stock_quote')
    @patch('handlers.market_data.stock_handlers.get_yfinance_session')
    def test_bulk_import_missing_columns(self, mock_session, mock_get_quote, mock_download):
        # Mock session
        mock_session.return_value = MagicMock()
        
        # Mock yf.download returning a DataFrame with missing columns for one symbol
        # Structure of yf.download result for multiple tickers is a MultiIndex DataFrame
        # For single ticker it might be different, but let's simulate the structure causing issues
        
        # Create a mock DataFrame that mimics the structure returned by yf.download
        # We need a DataFrame where accessing ['LBTYB'] returns a DataFrame missing 'Close'
        
        # Simulation:
        # dict-like access to the result of download
        mock_df = MagicMock()
        
        # When accessing the specific symbol, return a DF with missing columns
        bad_df = pd.DataFrame({'Volume': [1000]}) # Missing Close, Open
        
        def get_item(key):
            if key == 'LBTYB':
                return bad_df
            return pd.DataFrame()
            
        mock_df.__getitem__.side_effect = get_item
        mock_download.return_value = mock_df
        
        # Mock get_stock_quote to succeed so fallback works
        mock_get_quote.return_value = {'symbol': 'LBTYB', 'price': 10.5, 'name': 'Liberty Global'}
        
        # Run the function
        # We need a mock db session
        mock_db_session = MagicMock()
        
        print("Testing bulk import with missing columns...")
        try:
            result = stock_handlers.import_stocks_to_db(['LBTYB'], db_session=mock_db_session)
            print(f"Result: {result}")
            
            # Assertions
            self.assertEqual(result['imported'] + result['updated'], 1)
            self.assertEqual(result['errors'], 0)
            print("✅ Test Passed: Handled missing columns by falling back to single quote")
            
        except KeyError as e:
            print(f"❌ Test Failed: KeyError {e} was not caught")
            raise e
        except Exception as e:
            print(f"❌ Test Failed: Unexpected error {e}")
            raise e

if __name__ == '__main__':
    unittest.main()
