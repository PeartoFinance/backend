"""
Forecast Data Handler - YFinance Integration
Handles fetching and storing analyst recommendations, price targets, 
earnings estimates, and recommendation history for the Forecast tab.
"""

import yfinance as yf
from datetime import datetime
import logging
import pandas as pd
from models.base import db
from models.market import AnalystRecommendation, EarningsEstimate, RecommendationHistory

logger = logging.getLogger(__name__)


def sync_forecast_data(symbol: str):
    """
    Fetch analyst recommendations, price targets, earnings estimates, 
    and recommendation history from Yahoo Finance and save to database.
    
    Args:
        symbol: Stock ticker symbol (e.g., 'TSLA')
        
    Returns:
        Dictionary with status and summary of synced data
    """
    try:
        ticker = yf.Ticker(symbol)
        
        # 1. Get Price Targets
        targets = ticker.analyst_price_targets
        
        # 2. Get Recommendation Summary (Counts)
        rec_summary = ticker.recommendations_summary
        
        # 3. Get Recent Upgrades/Downgrades
        upgrades = ticker.upgrades_downgrades
        
        # Store current recommendation state
        today = datetime.utcnow().date()
        existing = AnalystRecommendation.query.filter_by(
            symbol=symbol,
            date=today
        ).first()
        
        recommendation = existing if existing else AnalystRecommendation(
            symbol=symbol,
            date=today
        )
        
        # Map Price Targets
        if targets:
            recommendation.target_high = targets.get('high')
            recommendation.target_low = targets.get('low')
            recommendation.target_mean = targets.get('mean')
            recommendation.target_median = targets.get('median')
            recommendation.current_price = targets.get('current')
            
        # Map Recommendation Summary (Counts)
        if rec_summary is not None and not rec_summary.empty:
            latest = rec_summary.iloc[0] if len(rec_summary) > 0 else None
            if latest is not None:
                recommendation.strong_buy = int(latest.get('strongBuy', 0))
                recommendation.buy = int(latest.get('buy', 0))
                recommendation.hold = int(latest.get('hold', 0))
                recommendation.sell = int(latest.get('sell', 0))
                recommendation.strong_sell = int(latest.get('strongSell', 0))
        
        # Map Latest Action
        if upgrades is not None and not upgrades.empty:
            latest_action = upgrades.iloc[0]
            recommendation.firm = latest_action.get('Firm')
            recommendation.to_grade = latest_action.get('ToGrade')
            recommendation.from_grade = latest_action.get('FromGrade')
            recommendation.action = latest_action.get('Action')

        if not existing:
            db.session.add(recommendation)
        
        # 4. Sync Earnings Estimates
        _sync_earnings_estimates(symbol, ticker)
        
        # 5. Sync Recommendation History
        _sync_recommendation_history(symbol, ticker)
            
        db.session.commit()
        logger.info(f"Successfully synced forecast data for {symbol}")
        return {
            'status': 'success', 
            'symbol': symbol,
            'targets': {
                'mean': float(recommendation.target_mean) if recommendation.target_mean else None,
                'high': float(recommendation.target_high) if recommendation.target_high else None,
                'low': float(recommendation.target_low) if recommendation.target_low else None
            }
        }

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error syncing forecast for {symbol}: {str(e)}")
        return {'status': 'error', 'message': str(e)}


def _sync_earnings_estimates(symbol: str, ticker):
    """Sync revenue and EPS estimates from yfinance."""
    try:
        # Revenue estimates DataFrame has:
        # - Index: fiscal periods like '0q', '+1q', '0y', '+1y'
        # - Columns: 'avg', 'low', 'high', 'numberOfAnalysts', 'growth', 'period'
        rev_est = ticker.revenue_estimate
        eps_est = ticker.earnings_estimate
        
        if rev_est is not None and not rev_est.empty:
            current_year = datetime.now().year
            
            for idx in rev_est.index:
                try:
                    fiscal_label = str(idx)  # e.g., '0q', '+1q', '0y', '+1y'
                    
                    # Determine period type and fiscal year from index
                    if 'y' in fiscal_label.lower():
                        period_type = 'annual'
                        # Parse year offset: '0y' = current year, '+1y' = next year
                        year_offset = int(fiscal_label.replace('y', '').replace('+', '').replace('-', '') or '0')
                        if '-' in fiscal_label:
                            year_offset = -year_offset
                        fiscal_year = f"FY{current_year + year_offset}"
                    elif 'q' in fiscal_label.lower():
                        period_type = 'quarterly'
                        # Parse quarter: '0q' = current quarter, '+1q' = next quarter
                        quarter_offset = int(fiscal_label.replace('q', '').replace('+', '').replace('-', '') or '0')
                        current_quarter = (datetime.now().month - 1) // 3 + 1
                        target_quarter = current_quarter + quarter_offset
                        target_year = current_year + (target_quarter - 1) // 4
                        target_quarter = ((target_quarter - 1) % 4) + 1
                        fiscal_year = f"Q{target_quarter} {target_year}"
                    else:
                        continue  # Skip unknown format
                    
                    # Check if entry exists
                    existing = EarningsEstimate.query.filter_by(
                        symbol=symbol,
                        period_type=period_type,
                        fiscal_year=fiscal_year
                    ).first()
                    
                    estimate = existing if existing else EarningsEstimate(
                        symbol=symbol,
                        period_type=period_type,
                        fiscal_year=fiscal_year
                    )
                    
                    # Get revenue row data
                    rev_row = rev_est.loc[idx]
                    if 'avg' in rev_row.index and pd.notna(rev_row['avg']):
                        estimate.revenue_avg = int(rev_row['avg'])
                    if 'low' in rev_row.index and pd.notna(rev_row['low']):
                        estimate.revenue_low = int(rev_row['low'])
                    if 'high' in rev_row.index and pd.notna(rev_row['high']):
                        estimate.revenue_high = int(rev_row['high'])
                    if 'numberOfAnalysts' in rev_row.index and pd.notna(rev_row['numberOfAnalysts']):
                        estimate.num_revenue_analysts = int(rev_row['numberOfAnalysts'])
                    if 'growth' in rev_row.index and pd.notna(rev_row['growth']):
                        estimate.revenue_growth = float(rev_row['growth'])
                    
                    # Get EPS row data if available
                    if eps_est is not None and not eps_est.empty and idx in eps_est.index:
                        eps_row = eps_est.loc[idx]
                        if 'avg' in eps_row.index and pd.notna(eps_row['avg']):
                            estimate.eps_avg = float(eps_row['avg'])
                        if 'low' in eps_row.index and pd.notna(eps_row['low']):
                            estimate.eps_low = float(eps_row['low'])
                        if 'high' in eps_row.index and pd.notna(eps_row['high']):
                            estimate.eps_high = float(eps_row['high'])
                        if 'numberOfAnalysts' in eps_row.index and pd.notna(eps_row['numberOfAnalysts']):
                            estimate.num_eps_analysts = int(eps_row['numberOfAnalysts'])
                        if 'growth' in eps_row.index and pd.notna(eps_row['growth']):
                            estimate.eps_growth = float(eps_row['growth'])
                    
                    if not existing:
                        db.session.add(estimate)
                        
                except Exception as row_err:
                    logger.warning(f"Error processing estimate row {idx} for {symbol}: {row_err}")
                    continue
                    
    except Exception as e:
        logger.warning(f"Could not sync earnings estimates for {symbol}: {e}")


def _sync_recommendation_history(symbol: str, ticker):
    """Sync historical recommendation trends from yfinance."""
    try:
        rec_summary = ticker.recommendations_summary
        
        if rec_summary is not None and not rec_summary.empty:
            for idx, row in rec_summary.iterrows():
                try:
                    # Parse period from index (e.g., '0m', '-1m', '-2m', etc.)
                    period_str = str(idx)
                    
                    # Calculate the month date
                    months_ago = 0
                    if 'm' in period_str:
                        months_ago = abs(int(period_str.replace('m', '').replace('-', '').replace('+', '') or '0'))
                    
                    # Get month date
                    today = datetime.now()
                    month_date = datetime(today.year, today.month, 1)
                    
                    # Go back months
                    for _ in range(months_ago):
                        month_date = datetime(month_date.year, month_date.month, 1) - pd.Timedelta(days=1)
                        month_date = datetime(month_date.year, month_date.month, 1)
                    
                    period_label = month_date.strftime("%b '%y")
                    
                    # Check if exists
                    existing = RecommendationHistory.query.filter_by(
                        symbol=symbol,
                        period_date=month_date.date()
                    ).first()
                    
                    history = existing if existing else RecommendationHistory(
                        symbol=symbol,
                        period_date=month_date.date(),
                        period_label=period_label
                    )
                    
                    history.strong_buy = int(row.get('strongBuy', 0))
                    history.buy = int(row.get('buy', 0))
                    history.hold = int(row.get('hold', 0))
                    history.sell = int(row.get('sell', 0))
                    history.strong_sell = int(row.get('strongSell', 0))
                    
                    if not existing:
                        db.session.add(history)
                        
                except Exception as row_err:
                    logger.warning(f"Error processing recommendation row {idx} for {symbol}: {row_err}")
                    continue
                    
    except Exception as e:
        logger.warning(f"Could not sync recommendation history for {symbol}: {e}")


def get_forecast_data(symbol: str):
    """Retrieve the latest forecast data from the database."""
    record = AnalystRecommendation.query.filter_by(symbol=symbol).order_by(AnalystRecommendation.date.desc()).first()
    return record.to_dict() if record else None


def get_detailed_forecast(symbol: str):
    """
    Get comprehensive forecast data including price targets, analyst consensus,
    earnings estimates, and recommendation history.
    """
    # Price targets & current consensus
    recommendation = AnalystRecommendation.query.filter_by(
        symbol=symbol
    ).order_by(AnalystRecommendation.date.desc()).first()
    
    # Earnings estimates (annual)
    annual_estimates = EarningsEstimate.query.filter_by(
        symbol=symbol,
        period_type='annual'
    ).order_by(EarningsEstimate.fiscal_year).all()
    
    # Earnings estimates (quarterly)
    quarterly_estimates = EarningsEstimate.query.filter_by(
        symbol=symbol,
        period_type='quarterly'
    ).order_by(EarningsEstimate.fiscal_year).all()
    
    # Recommendation history (last 12 months)
    rec_history = RecommendationHistory.query.filter_by(
        symbol=symbol
    ).order_by(RecommendationHistory.period_date.desc()).limit(12).all()
    
    # Calculate upside
    upside = None
    if recommendation and recommendation.target_mean and recommendation.current_price:
        target_mean = float(recommendation.target_mean)
        current = float(recommendation.current_price)
        if current > 0:
            upside = ((target_mean - current) / current) * 100
    
    # Determine consensus
    consensus = 'Hold'
    if recommendation:
        total = (recommendation.strong_buy or 0) + (recommendation.buy or 0) + \
                (recommendation.hold or 0) + (recommendation.sell or 0) + (recommendation.strong_sell or 0)
        if total > 0:
            bullish = (recommendation.strong_buy or 0) + (recommendation.buy or 0)
            bearish = (recommendation.sell or 0) + (recommendation.strong_sell or 0)
            if bullish > bearish * 2:
                consensus = 'Strong Buy'
            elif bullish > bearish:
                consensus = 'Buy'
            elif bearish > bullish:
                consensus = 'Sell'
    
    return {
        'priceTarget': {
            'low': float(recommendation.target_low) if recommendation and recommendation.target_low else None,
            'mean': float(recommendation.target_mean) if recommendation and recommendation.target_mean else None,
            'high': float(recommendation.target_high) if recommendation and recommendation.target_high else None,
            'current': float(recommendation.current_price) if recommendation and recommendation.current_price else None,
            'upside': round(upside, 2) if upside else None,
        },
        'analystConsensus': {
            'consensus': consensus,
            'strongBuy': recommendation.strong_buy if recommendation else 0,
            'buy': recommendation.buy if recommendation else 0,
            'hold': recommendation.hold if recommendation else 0,
            'sell': recommendation.sell if recommendation else 0,
            'strongSell': recommendation.strong_sell if recommendation else 0,
            'total': (
                (recommendation.strong_buy or 0) + (recommendation.buy or 0) +
                (recommendation.hold or 0) + (recommendation.sell or 0) + (recommendation.strong_sell or 0)
            ) if recommendation else 0,
        },
        'earningsEstimates': {
            'annual': [e.to_dict() for e in annual_estimates],
            'quarterly': [e.to_dict() for e in quarterly_estimates],
        },
        'recommendationTrends': [r.to_dict() for r in reversed(rec_history)],
    }
