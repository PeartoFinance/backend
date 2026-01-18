"""
Financial Data Handler - YFinance Integration
Handles fetching and storing historical financial statements (Income Statement, Balance Sheet, Cash Flow)
to support the Business Profile "Financials" tab.
"""

import yfinance as yf
from datetime import datetime
import logging
from models.base import db
from models.market import CompanyFinancials

logger = logging.getLogger(__name__)

def sync_financials(symbol: str, period: str = 'annual'):
    """
    Fetch financial statements from Yahoo Finance and save to database.
    
    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL')
        period: 'annual' or 'quarterly'
        
    Returns:
        Dictionary with status and number of records synced
    """
    try:
        ticker = yf.Ticker(symbol)
        
        # 1. Get the data from yfinance
        # .financials returns the Income Statement
        # .balance_sheet returns the Balance Sheet
        # .cashflow returns the Cash Flow statement
        if period == 'annual':
            income_stmt = ticker.financials
            balance_sheet = ticker.balance_sheet
            cash_flow = ticker.cashflow
        else:
            income_stmt = ticker.quarterly_financials
            balance_sheet = ticker.quarterly_balance_sheet
            cash_flow = ticker.quarterly_cashflow

        if income_stmt.empty:
            return {'status': 'error', 'message': f'No financial data found for {symbol}'}

        synced_count = 0
        
        # 2. Iterate through the columns (dates) in the financial statements
        # yfinance returns dates as columns in a DataFrame
        for date_col in income_stmt.columns:
            fiscal_date = date_col.date()
            
            # Check if we already have this record to avoid duplicates
            existing = CompanyFinancials.query.filter_by(
                symbol=symbol,
                period=period,
                fiscal_date_ending=fiscal_date
            ).first()
            
            # Extract values safely (using .get() or checking index)
            # Note: Index names in yfinance can vary slightly, but these are standard
            def get_val(df, key):
                try:
                    if key in df.index:
                        val = df.loc[key, date_col]
                        return int(val) if not hasattr(val, '__len__') and val == val else None
                    return None
                except Exception:
                    return None

            # 3. Create or Update the record
            financial = existing if existing else CompanyFinancials(
                symbol=symbol,
                period=period,
                fiscal_date_ending=fiscal_date
            )
            
            # Map Income Statement fields
            financial.revenue = get_val(income_stmt, 'Total Revenue')
            financial.net_income = get_val(income_stmt, 'Net Income')
            financial.gross_profit = get_val(income_stmt, 'Gross Profit')
            financial.ebitda = get_val(income_stmt, 'EBITDA')
            financial.operating_income = get_val(income_stmt, 'Operating Income')
            
            # Map Balance Sheet fields
            financial.total_assets = get_val(balance_sheet, 'Total Assets')
            financial.total_liabilities = get_val(balance_sheet, 'Total Liabilities Net Minority Interest')
            financial.shareholder_equity = get_val(balance_sheet, 'Stockholders Equity')
            financial.cash_and_equivalents = get_val(balance_sheet, 'Cash And Cash Equivalents')
            financial.total_debt = get_val(balance_sheet, 'Total Debt')
            
            # Map Cash Flow fields
            financial.operating_cash_flow = get_val(cash_flow, 'Operating Cash Flow')
            financial.capital_expenditure = get_val(cash_flow, 'Capital Expenditure')
            financial.free_cash_flow = get_val(cash_flow, 'Free Cash Flow')
            
            # Map EPS (if available in financials)
            financial.eps_actual = get_val(income_stmt, 'Basic EPS')
            
            if not existing:
                db.session.add(financial)
            
            synced_count += 1

        db.session.commit()
        logger.info(f"Successfully synced {synced_count} {period} financial records for {symbol}")
        return {'status': 'success', 'count': synced_count}

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error syncing financials for {symbol}: {str(e)}")
        return {'status': 'error', 'message': str(e)}

def get_company_financials(symbol: str, period: str = 'annual', limit: int = 4):
    """
    Retrieve stored financials from the database for the API.
    """
    records = CompanyFinancials.query.filter_by(
        symbol=symbol, 
        period=period
    ).order_by(CompanyFinancials.fiscal_date_ending.desc()).limit(limit).all()
    
    return [r.to_dict() for r in records]
