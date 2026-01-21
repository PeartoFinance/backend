"""
Financial Data Handler - YFinance Integration (Database-Backed)
Syncs comprehensive financial statements to database.
"""

import yfinance as yf
from datetime import datetime
import logging
from typing import Optional, Dict, Any, List
from models.base import db
from models.market import CompanyFinancials

logger = logging.getLogger(__name__)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _safe_value(val) -> Optional[float]:
    """Convert value to float safely, handling NaN and None"""
    if val is None:
        return None
    try:
        import math
        if math.isnan(val):
            return None
        return float(val)
    except (ValueError, TypeError):
        return None


def _safe_int(val) -> Optional[int]:
    """Convert value to int safely"""
    if val is None:
        return None
    try:
        import math
        if math.isnan(val):
            return None
        return int(val)
    except (ValueError, TypeError):
        return None


def _calc_margin(numerator, denominator) -> Optional[float]:
    """Calculate margin as percentage"""
    if numerator is None or denominator is None or denominator == 0:
        return None
    return round((numerator / denominator) * 100, 2)


# =============================================================================
# SYNC FUNCTIONS - Save to Database
# =============================================================================

def sync_financials(symbol: str, period: str = 'annual') -> Dict[str, Any]:
    """
    Sync comprehensive financial statements from yfinance to database.
    
    Args:
        symbol: Stock ticker (e.g., 'AAPL')
        period: 'annual' or 'quarterly'
    """
    logger.info(f"Syncing {period} financials for {symbol}")
    
    try:
        ticker = yf.Ticker(symbol)
        
        # Fetch all statements
        if period == 'annual':
            income_df = ticker.income_stmt
            balance_df = ticker.balance_sheet
            cashflow_df = ticker.cashflow
        else:
            income_df = ticker.quarterly_income_stmt
            balance_df = ticker.quarterly_balance_sheet
            cashflow_df = ticker.quarterly_cashflow

        if income_df is None or income_df.empty:
            return {'status': 'error', 'message': f'No {period} data for {symbol}'}

        synced_count = 0
        
        # Process each fiscal period (columns are dates)
        for date_col in income_df.columns:
            fiscal_date = date_col.date()
            
            # Find or create record
            record = CompanyFinancials.query.filter_by(
                symbol=symbol,
                period=period,
                fiscal_date_ending=fiscal_date
            ).first()
            
            is_new = record is None
            if is_new:
                record = CompanyFinancials(
                    symbol=symbol,
                    period=period,
                    fiscal_date_ending=fiscal_date
                )
            
            # Helper to get value from dataframe
            def get_income(key):
                return _safe_int(income_df.loc[key, date_col]) if key in income_df.index else None
            
            def get_balance(key):
                if balance_df is None or balance_df.empty:
                    return None
                return _safe_int(balance_df.loc[key, date_col]) if key in balance_df.index and date_col in balance_df.columns else None
            
            def get_cashflow(key):
                if cashflow_df is None or cashflow_df.empty:
                    return None
                return _safe_int(cashflow_df.loc[key, date_col]) if key in cashflow_df.index and date_col in cashflow_df.columns else None
            
            # =============================================
            # INCOME STATEMENT
            # =============================================
            record.revenue = get_income('Total Revenue')
            record.cost_of_revenue = get_income('Cost Of Revenue')
            record.gross_profit = get_income('Gross Profit')
            record.selling_general_admin = get_income('Selling General And Administration')
            record.research_development = get_income('Research And Development')
            record.operating_expenses = get_income('Operating Expense')
            record.operating_income = get_income('Operating Income')
            record.interest_expense = get_income('Interest Expense')
            record.interest_income = get_income('Interest Income')
            record.pretax_income = get_income('Pretax Income')
            record.income_tax = get_income('Tax Provision')
            record.net_income = get_income('Net Income')
            record.net_income_common = get_income('Net Income Common Stockholders')
            record.ebitda = get_income('EBITDA')
            record.ebit = get_income('EBIT')
            
            # EPS & Shares
            record.eps_basic = _safe_value(income_df.loc['Basic EPS', date_col]) if 'Basic EPS' in income_df.index else None
            record.eps_diluted = _safe_value(income_df.loc['Diluted EPS', date_col]) if 'Diluted EPS' in income_df.index else None
            record.shares_basic = get_income('Basic Average Shares')
            record.shares_diluted = get_income('Diluted Average Shares')
            
            # Calculate Margins
            record.gross_margin = _calc_margin(record.gross_profit, record.revenue)
            record.operating_margin = _calc_margin(record.operating_income, record.revenue)
            record.profit_margin = _calc_margin(record.net_income, record.revenue)
            
            # =============================================
            # BALANCE SHEET
            # =============================================
            record.cash_and_equivalents = get_balance('Cash And Cash Equivalents')
            record.short_term_investments = get_balance('Short Term Investments')
            record.accounts_receivable = get_balance('Accounts Receivable')
            record.inventory = get_balance('Inventory')
            record.current_assets = get_balance('Current Assets')
            record.property_plant_equipment = get_balance('Net PPE')
            record.long_term_investments = get_balance('Long Term Investments')
            record.goodwill = get_balance('Goodwill')
            record.intangible_assets = get_balance('Other Intangible Assets')
            record.total_assets = get_balance('Total Assets')
            
            record.accounts_payable = get_balance('Accounts Payable')
            record.short_term_debt = get_balance('Current Debt')
            record.current_liabilities = get_balance('Current Liabilities')
            record.long_term_debt = get_balance('Long Term Debt')
            record.total_liabilities = get_balance('Total Liabilities Net Minority Interest')
            record.total_debt = get_balance('Total Debt')
            
            record.common_stock = get_balance('Common Stock')
            record.retained_earnings = get_balance('Retained Earnings')
            record.shareholder_equity = get_balance('Stockholders Equity')
            
            # Computed Balance Sheet metrics
            if record.current_assets and record.current_liabilities:
                record.working_capital = record.current_assets - record.current_liabilities
            
            cash_total = (record.cash_and_equivalents or 0) + (record.short_term_investments or 0)
            if cash_total or record.total_debt:
                record.net_cash = cash_total - (record.total_debt or 0)
            
            # =============================================
            # CASH FLOW
            # =============================================
            record.depreciation_amortization = get_cashflow('Depreciation And Amortization')
            record.stock_based_compensation = get_cashflow('Stock Based Compensation')
            record.change_in_working_capital = get_cashflow('Change In Working Capital')
            record.operating_cash_flow = get_cashflow('Operating Cash Flow')
            record.capital_expenditure = get_cashflow('Capital Expenditure')
            record.investing_cash_flow = get_cashflow('Investing Cash Flow')
            record.debt_issued = get_cashflow('Issuance Of Debt')
            record.debt_repaid = get_cashflow('Repayment Of Debt')
            record.dividends_paid = get_cashflow('Common Stock Dividend Paid')
            record.stock_repurchased = get_cashflow('Repurchase Of Capital Stock')
            record.financing_cash_flow = get_cashflow('Financing Cash Flow')
            record.free_cash_flow = get_cashflow('Free Cash Flow')
            record.net_cash_flow = get_cashflow('Changes In Cash')
            
            # Calculate Free Cash Flow if not present
            if record.free_cash_flow is None and record.operating_cash_flow and record.capital_expenditure:
                record.free_cash_flow = record.operating_cash_flow + record.capital_expenditure
            
            if is_new:
                db.session.add(record)
            
            synced_count += 1

        db.session.commit()
        logger.info(f"Successfully synced {synced_count} {period} records for {symbol}")
        return {'status': 'success', 'count': synced_count}

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error syncing financials for {symbol}: {e}")
        return {'status': 'error', 'message': str(e)}


def sync_all_financials(symbol: str) -> Dict[str, Any]:
    """Sync both annual and quarterly financials for a symbol"""
    annual_result = sync_financials(symbol, 'annual')
    quarterly_result = sync_financials(symbol, 'quarterly')
    
    return {
        'status': 'success' if annual_result['status'] == 'success' else 'partial',
        'annual': annual_result,
        'quarterly': quarterly_result
    }


# =============================================================================
# READ FUNCTIONS - Return from Database
# =============================================================================

def get_company_financials(symbol: str, period: str = 'annual', limit: int = 10) -> List[Dict]:
    """Get financials from database"""
    records = CompanyFinancials.query.filter_by(
        symbol=symbol, 
        period=period
    ).order_by(CompanyFinancials.fiscal_date_ending.desc()).limit(limit).all()
    
    return [r.to_dict() for r in records]


def get_financial_statements(symbol: str, statement_type: str = 'income', period: str = 'annual') -> Dict[str, Any]:
    """
    Get formatted financial statements from database for frontend display.
    Returns data in multi-column format like stockanalysis.com.
    """
    records = CompanyFinancials.query.filter_by(
        symbol=symbol,
        period=period
    ).order_by(CompanyFinancials.fiscal_date_ending.desc()).limit(10).all()
    
    if not records:
        # Fallback: try to sync from yfinance
        sync_result = sync_financials(symbol, period)
        if sync_result.get('status') == 'success':
            records = CompanyFinancials.query.filter_by(
                symbol=symbol,
                period=period
            ).order_by(CompanyFinancials.fiscal_date_ending.desc()).limit(10).all()
    
    if not records:
        return {'periods': [], 'data': {}, 'error': 'No data available'}
    
    # Format period labels
    periods = []
    for r in records:
        if r.fiscal_date_ending:
            year = r.fiscal_date_ending.year
            if period == 'quarterly':
                month = r.fiscal_date_ending.month
                quarter = (month - 1) // 3 + 1
                periods.append(f"Q{quarter} {year}")
            else:
                periods.append(f"FY {year}")
        else:
            periods.append('N/A')
    
    # Build data based on statement type
    if statement_type == 'income':
        data = _format_income_statement(records)
    elif statement_type == 'balance':
        data = _format_balance_sheet(records)
    elif statement_type == 'cash_flow':
        data = _format_cash_flow(records)
    elif statement_type == 'ratios':
        return _get_ratios_from_db(symbol)
    elif statement_type == 'kpis':
        data = _format_kpis(records)
    else:
        data = {}
    
    return {
        'statementType': statement_type,
        'period': period,
        'periods': periods,
        'data': data,
        'symbol': symbol,
        'currency': 'USD'
    }


def _format_income_statement(records: List[CompanyFinancials]) -> Dict[str, List]:
    """Format income statement data for frontend"""
    return {
        'Revenue': [r.revenue for r in records],
        'Cost of Revenue': [r.cost_of_revenue for r in records],
        'Gross Profit': [r.gross_profit for r in records],
        'Gross Margin': [f"{r.gross_margin}%" if r.gross_margin else None for r in records],
        'Selling, General & Admin': [r.selling_general_admin for r in records],
        'Research & Development': [r.research_development for r in records],
        'Operating Expenses': [r.operating_expenses for r in records],
        'Operating Income': [r.operating_income for r in records],
        'Operating Margin': [f"{r.operating_margin}%" if r.operating_margin else None for r in records],
        'Interest Expense': [r.interest_expense for r in records],
        'Interest Income': [r.interest_income for r in records],
        'Pretax Income': [r.pretax_income for r in records],
        'Income Tax': [r.income_tax for r in records],
        'Net Income': [r.net_income for r in records],
        'Profit Margin': [f"{r.profit_margin}%" if r.profit_margin else None for r in records],
        'EPS (Basic)': [float(r.eps_basic) if r.eps_basic else None for r in records],
        'EPS (Diluted)': [float(r.eps_diluted) if r.eps_diluted else None for r in records],
        'Shares Outstanding (Basic)': [r.shares_basic for r in records],
        'Shares Outstanding (Diluted)': [r.shares_diluted for r in records],
        'EBITDA': [r.ebitda for r in records],
        'EBIT': [r.ebit for r in records],
    }


def _format_balance_sheet(records: List[CompanyFinancials]) -> Dict[str, List]:
    """Format balance sheet data for frontend"""
    return {
        'Cash & Equivalents': [r.cash_and_equivalents for r in records],
        'Short-Term Investments': [r.short_term_investments for r in records],
        'Accounts Receivable': [r.accounts_receivable for r in records],
        'Inventory': [r.inventory for r in records],
        'Total Current Assets': [r.current_assets for r in records],
        'Property, Plant & Equipment': [r.property_plant_equipment for r in records],
        'Long-Term Investments': [r.long_term_investments for r in records],
        'Goodwill': [r.goodwill for r in records],
        'Intangible Assets': [r.intangible_assets for r in records],
        'Total Assets': [r.total_assets for r in records],
        'Accounts Payable': [r.accounts_payable for r in records],
        'Short-Term Debt': [r.short_term_debt for r in records],
        'Total Current Liabilities': [r.current_liabilities for r in records],
        'Long-Term Debt': [r.long_term_debt for r in records],
        'Total Liabilities': [r.total_liabilities for r in records],
        'Total Debt': [r.total_debt for r in records],
        'Common Stock': [r.common_stock for r in records],
        'Retained Earnings': [r.retained_earnings for r in records],
        "Shareholders' Equity": [r.shareholder_equity for r in records],
        'Working Capital': [r.working_capital for r in records],
        'Net Cash (Debt)': [r.net_cash for r in records],
    }


def _format_cash_flow(records: List[CompanyFinancials]) -> Dict[str, List]:
    """Format cash flow data for frontend"""
    return {
        'Net Income': [r.net_income for r in records],
        'Depreciation & Amortization': [r.depreciation_amortization for r in records],
        'Stock-Based Compensation': [r.stock_based_compensation for r in records],
        'Change in Working Capital': [r.change_in_working_capital for r in records],
        'Operating Cash Flow': [r.operating_cash_flow for r in records],
        'Capital Expenditures': [r.capital_expenditure for r in records],
        'Investing Cash Flow': [r.investing_cash_flow for r in records],
        'Debt Issued': [r.debt_issued for r in records],
        'Debt Repaid': [r.debt_repaid for r in records],
        'Dividends Paid': [r.dividends_paid for r in records],
        'Stock Repurchased': [r.stock_repurchased for r in records],
        'Financing Cash Flow': [r.financing_cash_flow for r in records],
        'Free Cash Flow': [r.free_cash_flow for r in records],
        'Net Cash Flow': [r.net_cash_flow for r in records],
    }


def _format_kpis(records: List[CompanyFinancials]) -> Dict[str, List]:
    """Format key performance indicators from database records"""
    # Use stored margin values where available, otherwise calculate
    gross_margins = []
    operating_margins = []
    net_margins = []
    revenue_growth = []
    eps_list = []
    roe_list = []
    roa_list = []
    debt_equity = []
    
    prev_revenue = None
    for r in records:
        # Use stored margins if available, otherwise calculate
        if r.gross_margin:
            gross_margins.append(float(r.gross_margin))
        elif r.revenue and r.gross_profit:
            gross_margins.append(round(r.gross_profit / r.revenue * 100, 2))
        else:
            gross_margins.append(None)
            
        if r.operating_margin:
            operating_margins.append(float(r.operating_margin))
        elif r.revenue and r.operating_income:
            operating_margins.append(round(r.operating_income / r.revenue * 100, 2))
        else:
            operating_margins.append(None)
            
        if r.profit_margin:
            net_margins.append(float(r.profit_margin))
        elif r.revenue and r.net_income:
            net_margins.append(round(r.net_income / r.revenue * 100, 2))
        else:
            net_margins.append(None)
        
        # Revenue Growth YoY
        if prev_revenue and r.revenue:
            growth = round((prev_revenue - r.revenue) / abs(r.revenue) * 100, 2)
            revenue_growth.append(growth)
        else:
            revenue_growth.append(None)
        prev_revenue = r.revenue
        
        # EPS
        eps_list.append(float(r.eps_diluted) if r.eps_diluted else None)
        
        # ROE (Net Income / Shareholder Equity)
        if r.net_income and r.shareholder_equity and r.shareholder_equity != 0:
            roe_list.append(round(r.net_income / r.shareholder_equity * 100, 2))
        else:
            roe_list.append(None)
            
        # ROA (Net Income / Total Assets)
        if r.net_income and r.total_assets and r.total_assets != 0:
            roa_list.append(round(r.net_income / r.total_assets * 100, 2))
        else:
            roa_list.append(None)
            
        # Debt to Equity
        if r.total_debt and r.shareholder_equity and r.shareholder_equity != 0:
            debt_equity.append(round(r.total_debt / r.shareholder_equity, 2))
        else:
            debt_equity.append(None)
    
    return {
        'Gross Margin (%)': gross_margins,
        'Operating Margin (%)': operating_margins,
        'Net Margin (%)': net_margins,
        'Revenue Growth (%)': revenue_growth,
        'EPS (Diluted)': eps_list,
        'Return on Equity (%)': roe_list,
        'Return on Assets (%)': roa_list,
        'Debt to Equity': debt_equity,
    }


def _get_ratios_from_db(symbol: str) -> Dict[str, Any]:
    """Get ratios from yfinance (these are real-time metrics)"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info or {}
        
        ratios = {
            'Valuation': {
                'Market Cap': _safe_value(info.get('marketCap')),
                'Enterprise Value': _safe_value(info.get('enterpriseValue')),
                'PE Ratio (TTM)': _safe_value(info.get('trailingPE')),
                'Forward PE': _safe_value(info.get('forwardPE')),
                'Price/Sales': _safe_value(info.get('priceToSalesTrailing12Months')),
                'Price/Book': _safe_value(info.get('priceToBook')),
                'EV/EBITDA': _safe_value(info.get('enterpriseToEbitda')),
            },
            'Profitability': {
                'Gross Margin': f"{round(_safe_value(info.get('grossMargins', 0)) * 100, 2)}%" if info.get('grossMargins') else None,
                'Operating Margin': f"{round(_safe_value(info.get('operatingMargins', 0)) * 100, 2)}%" if info.get('operatingMargins') else None,
                'Profit Margin': f"{round(_safe_value(info.get('profitMargins', 0)) * 100, 2)}%" if info.get('profitMargins') else None,
                'ROE': f"{round(_safe_value(info.get('returnOnEquity', 0)) * 100, 2)}%" if info.get('returnOnEquity') else None,
                'ROA': f"{round(_safe_value(info.get('returnOnAssets', 0)) * 100, 2)}%" if info.get('returnOnAssets') else None,
            },
            'Liquidity': {
                'Current Ratio': _safe_value(info.get('currentRatio')),
                'Quick Ratio': _safe_value(info.get('quickRatio')),
                'Debt/Equity': _safe_value(info.get('debtToEquity')),
            },
            'Per Share': {
                'EPS (TTM)': _safe_value(info.get('trailingEps')),
                'Book Value/Share': _safe_value(info.get('bookValue')),
                'Revenue/Share': _safe_value(info.get('revenuePerShare')),
            },
            'Dividends': {
                'Dividend Rate': _safe_value(info.get('dividendRate')),
                'Dividend Yield': f"{round(_safe_value(info.get('dividendYield', 0)) * 100, 2)}%" if info.get('dividendYield') else None,
                'Payout Ratio': f"{round(_safe_value(info.get('payoutRatio', 0)) * 100, 2)}%" if info.get('payoutRatio') else None,
            },
        }
        
        return {'statementType': 'ratios', 'data': ratios, 'symbol': symbol}
    except Exception as e:
        logger.error(f"Error getting ratios for {symbol}: {e}")
        return {'statementType': 'ratios', 'data': {}, 'error': str(e)}
