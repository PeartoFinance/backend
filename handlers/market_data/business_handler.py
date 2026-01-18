"""
Business Profile Handler
Manages high-level business profile settings, including visibility (listing),
featured status, and manual market issues/alerts.
"""

import logging
from datetime import datetime
from models.base import db
from models.market import MarketData, MarketIssue

logger = logging.getLogger(__name__)

def toggle_business_listing(symbol: str, is_listed: bool):
    """
    Enable or disable a company's visibility in the public Business Profile directory.
    
    Args:
        symbol: Stock ticker symbol
        is_listed: True to show in public directory, False to hide
    """
    try:
        business = MarketData.query.filter_by(symbol=symbol).first()
        if not business:
            return {'status': 'error', 'message': f'Business with symbol {symbol} not found'}
        
        business.is_listed = is_listed
        db.session.commit()
        
        status_text = "listed" if is_listed else "unlisted"
        logger.info(f"Business {symbol} has been {status_text}")
        return {'status': 'success', 'message': f'Business {symbol} is now {status_text}'}
    except Exception as e:
        db.session.rollback()
        return {'status': 'error', 'message': str(e)}

def add_market_issue(symbol: str, title: str, description: str, severity: str = 'info'):
    """
    Add a manual alert or "Market Issue" to a company's profile.
    Used for regulatory warnings, liquidity issues, etc.
    """
    try:
        # Check if business exists
        business = MarketData.query.filter_by(symbol=symbol).first()
        if not business:
            return {'status': 'error', 'message': f'Cannot add issue: Symbol {symbol} not found'}

        issue = MarketIssue(
            symbol=symbol,
            title=title,
            description=description,
            severity=severity,
            issue_date=datetime.utcnow().date(),
            is_active=True
        )
        
        db.session.add(issue)
        db.session.commit()
        
        logger.info(f"Added {severity} issue for {symbol}: {title}")
        return {'status': 'success', 'issue_id': issue.id}
    except Exception as e:
        db.session.rollback()
        return {'status': 'error', 'message': str(e)}

def resolve_market_issue(issue_id: int):
    """
    Mark a market issue as resolved (inactive).
    """
    try:
        issue = MarketIssue.query.get(issue_id)
        if not issue:
            return {'status': 'error', 'message': 'Issue not found'}
        
        issue.is_active = False
        db.session.commit()
        return {'status': 'success', 'message': 'Issue marked as resolved'}
    except Exception as e:
        db.session.rollback()
        return {'status': 'error', 'message': str(e)}

def get_business_directory(search: str = None, country: str = 'US', limit: int = 50):
    """
    Get a list of all businesses that are marked as 'is_listed'.
    Used for the public Business Directory page.
    """
    query = MarketData.query.filter_by(is_listed=True)
    
    if country:
        query = query.filter((MarketData.country_code == country) | (MarketData.country_code == 'GLOBAL'))
    
    if search:
        query = query.filter(
            db.or_(
                MarketData.symbol.ilike(f'%{search}%'),
                MarketData.name.ilike(f'%{search}%')
            )
        )
        
    businesses = query.order_by(MarketData.name).limit(limit).all()
    return [b.to_dict() for b in businesses]
