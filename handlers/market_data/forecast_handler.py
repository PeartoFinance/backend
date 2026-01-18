"""
Forecast Data Handler - YFinance Integration
Handles fetching and storing analyst recommendations and price targets
to support the Business Profile "Forecast" tab.
"""

import yfinance as yf
from datetime import datetime
import logging
from models.base import db
from models.market import AnalystRecommendation

logger = logging.getLogger(__name__)

def sync_forecast_data(symbol: str):
    """
    Fetch analyst recommendations and price targets from Yahoo Finance and save to database.
    
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
        
        # We store a summary record for the current state
        # Check if we already have a recent record for today
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

def get_forecast_data(symbol: str):
    """
    Retrieve the latest forecast data from the database.
    """
    record = AnalystRecommendation.query.filter_by(symbol=symbol).order_by(AnalystRecommendation.date.desc()).first()
    return record.to_dict() if record else None
