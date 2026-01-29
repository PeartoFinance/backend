"""
Calendar Data Handler - YFinance Integration
Functions for fetching earnings, IPO, splits, and economic calendar data
"""
import yfinance as yf
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any
import logging
import uuid

logger = logging.getLogger(__name__)


def get_earnings_calendar(
    start: str = None, 
    end: str = None, 
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Get earnings calendar for upcoming/recent earnings reports.
    
    Args:
        start: Start date (YYYY-MM-DD), defaults to today
        end: End date (YYYY-MM-DD), defaults to 7 days from start
        limit: Maximum number of results (YF caps at 100)
    
    Returns:
        List of earnings event dictionaries
    """
    try:
        calendars = yf.Calendars()
        
        kwargs = {'limit': min(limit, 100)}
        if start:
            kwargs['start'] = start
        if end:
            kwargs['end'] = end
        
        earnings_df = calendars.get_earnings_calendar(**kwargs)
        
        if earnings_df is None or earnings_df.empty:
            return []
        
        results = []
        for idx, row in earnings_df.iterrows():
            results.append({
                'symbol': row.get('ticker') or row.get('symbol'),
                'companyName': row.get('companyshortname') or row.get('company'),
                'earningsDate': row.get('startdatetime') or row.get('startdatetimetype'),
                'epsEstimate': row.get('epsestimate'),
                'epsActual': row.get('epsactual'),
                'epsSurprisePercent': row.get('epssurprisepct'),
                'revenueEstimate': row.get('revenueestimate'),
                'revenueActual': row.get('revenueactual'),
                'marketCap': row.get('marketcap'),
                'beforeAfterMarket': row.get('startdatetimetype'),
            })
        
        return results
    except Exception as e:
        logger.error(f"Error fetching earnings calendar: {e}")
        return []


def get_ipo_calendar(
    start: str = None, 
    end: str = None, 
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Get IPO calendar for upcoming/recent initial public offerings.
    
    Args:
        start: Start date (YYYY-MM-DD), defaults to today
        end: End date (YYYY-MM-DD), defaults to 7 days from start
        limit: Maximum number of results
    
    Returns:
        List of IPO event dictionaries
    """
    try:
        calendars = yf.Calendars()
        
        kwargs = {'limit': min(limit, 100)}
        if start:
            kwargs['start'] = start
        if end:
            kwargs['end'] = end
        
        ipo_df = calendars.get_ipo_info_calendar(**kwargs)
        
        if ipo_df is None or ipo_df.empty:
            return []
        
        results = []
        for idx, row in ipo_df.iterrows():
            results.append({
                'symbol': row.get('ticker') or row.get('symbol'),
                'companyName': row.get('companyname') or row.get('company'),
                'exchange': row.get('exchange'),
                'filingDate': row.get('filingdate'),
                'priceRange': row.get('pricerange'),
                'sharesOffered': row.get('shares'),
                'dealType': row.get('dealtype'),
                'pricedDate': row.get('priceddate'),
                'offerPrice': row.get('offerprice'),
            })
        
        return results
    except Exception as e:
        logger.error(f"Error fetching IPO calendar: {e}")
        return []


def get_splits_calendar(
    start: str = None, 
    end: str = None, 
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Get stock splits calendar.
    
    Args:
        start: Start date (YYYY-MM-DD)
        end: End date (YYYY-MM-DD)
        limit: Maximum number of results
    
    Returns:
        List of stock split event dictionaries
    """
    try:
        calendars = yf.Calendars()
        
        kwargs = {'limit': min(limit, 100)}
        if start:
            kwargs['start'] = start
        if end:
            kwargs['end'] = end
        
        splits_df = calendars.get_splits_calendar(**kwargs)
        
        if splits_df is None or splits_df.empty:
            return []
        
        results = []
        for idx, row in splits_df.iterrows():
            # Parse split ratio
            split_ratio = row.get('splitratio', '')
            numerator = None
            denominator = None
            if split_ratio and ':' in str(split_ratio):
                parts = str(split_ratio).split(':')
                if len(parts) == 2:
                    try:
                        numerator = int(parts[0])
                        denominator = int(parts[1])
                    except ValueError:
                        pass
            
            results.append({
                'symbol': row.get('ticker') or row.get('symbol'),
                'companyName': row.get('companyshortname'),
                'splitDate': row.get('date') or idx,
                'splitRatio': split_ratio,
                'numerator': numerator,
                'denominator': denominator,
                'announcementDate': row.get('announcementdate'),
            })
        
        return results
    except Exception as e:
        logger.error(f"Error fetching splits calendar: {e}")
        return []


def get_economic_events(
    start: str = None, 
    end: str = None, 
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Get economic events calendar (Fed meetings, GDP releases, etc.).
    
    Args:
        start: Start date (YYYY-MM-DD)
        end: End date (YYYY-MM-DD)
        limit: Maximum number of results
    
    Returns:
        List of economic event dictionaries
    """
    try:
        calendars = yf.Calendars()
        
        kwargs = {'limit': min(limit, 100)}
        if start:
            kwargs['start'] = start
        if end:
            kwargs['end'] = end
        
        events_df = calendars.get_economic_events_calendar(**kwargs)
        
        if events_df is None or events_df.empty:
            return []
        
        results = []
        for idx, row in events_df.iterrows():
            # yfinance returns: Region, Event Time, For, Actual, Expected, Last, Revised
            # The event name is in the index
            event_name = str(idx) if isinstance(idx, str) else row.name if hasattr(row, 'name') else 'Unknown'
            
            # Parse event time - may contain date and time info
            event_time = row.get('Event Time')
            event_date = None
            if event_time is not None:
                try:
                    # Event Time might be a timestamp or string
                    if hasattr(event_time, 'isoformat'):
                        event_date = event_time.isoformat()
                    else:
                        event_date = str(event_time)
                except:
                    event_date = None
            
            # Helper to safely convert values (handles NaN)
            def safe_value(v):
                if v is None:
                    return None
                import math
                try:
                    if math.isnan(float(v)):
                        return None
                except (ValueError, TypeError):
                    pass
                return str(v) if v is not None else None
            
            results.append({
                'id': str(uuid.uuid4()),
                'title': event_name.strip() if event_name else 'Unknown Event',
                'country': row.get('Region', ''),
                'eventDate': event_date,
                'importance': _map_importance(row.get('importance', 2)),  # Default medium
                'forecast': safe_value(row.get('Expected')),
                'previous': safe_value(row.get('Last')),
                'actual': safe_value(row.get('Actual')),
                'period': row.get('For', ''),
                'source': 'Yahoo Finance',
            })
        
        return results
    except Exception as e:
        logger.error(f"Error fetching economic events: {e}")
        return []


def _map_importance(value) -> str:
    """Map numeric importance to string."""
    if value is None:
        return 'medium'
    try:
        v = int(value)
        if v <= 1:
            return 'low'
        elif v == 2:
            return 'medium'
        else:
            return 'high'
    except (ValueError, TypeError):
        return 'medium'


def import_earnings_to_db(
    start: str = None, 
    end: str = None, 
    limit: int = 50, 
    db_session=None
) -> Dict[str, int]:
    """
    Import earnings calendar to database.
    
    Returns:
        Dictionary with counts of imported and updated records
    """
    from models import db, EarningsCalendar
    
    session = db_session or db.session
    imported = 0
    updated = 0
    errors = 0
    
    earnings = get_earnings_calendar(start, end, limit)
    
    for event in earnings:
        try:
            symbol = event.get('symbol')
            if not symbol:
                continue
            
            earnings_date = event.get('earningsDate')
            if isinstance(earnings_date, str):
                try:
                    earnings_date = datetime.fromisoformat(earnings_date.replace('Z', '+00:00'))
                except:
                    earnings_date = datetime.utcnow()
            
            # Check if exists
            existing = EarningsCalendar.query.filter_by(
                symbol=symbol,
                earnings_date=earnings_date
            ).first()
            
            if existing:
                existing.company_name = event.get('companyName')
                existing.eps_estimate = event.get('epsEstimate')
                existing.eps_actual = event.get('epsActual')
                existing.surprise_percent = event.get('epsSurprisePercent')
                existing.revenue_estimate = event.get('revenueEstimate')
                existing.revenue_actual = event.get('revenueActual')
                existing.market_cap = event.get('marketCap')
                existing.before_after_market = event.get('beforeAfterMarket')
                updated += 1
            else:
                new_earnings = EarningsCalendar(
                    symbol=symbol,
                    company_name=event.get('companyName'),
                    earnings_date=earnings_date,
                    eps_estimate=event.get('epsEstimate'),
                    eps_actual=event.get('epsActual'),
                    surprise_percent=event.get('epsSurprisePercent'),
                    revenue_estimate=event.get('revenueEstimate'),
                    revenue_actual=event.get('revenueActual'),
                    market_cap=event.get('marketCap'),
                    before_after_market=event.get('beforeAfterMarket'),
                )
                session.add(new_earnings)
                imported += 1
        except Exception as e:
            logger.error(f"Error importing earnings event: {e}")
            errors += 1
    
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Error committing earnings to database: {e}")
        return {'imported': 0, 'updated': 0, 'errors': len(earnings)}
    
    return {'imported': imported, 'updated': updated, 'errors': errors}


def import_ipos_to_db(
    start: str = None, 
    end: str = None, 
    limit: int = 50, 
    db_session=None
) -> Dict[str, int]:
    """
    Import IPO calendar to database.
    
    Returns:
        Dictionary with counts of imported and updated records
    """
    from models import db, StockOffer
    
    session = db_session or db.session
    imported = 0
    updated = 0
    errors = 0
    
    ipos = get_ipo_calendar(start, end, limit)
    
    for ipo in ipos:
        try:
            symbol = ipo.get('symbol')
            company_name = ipo.get('companyName')
            if not company_name:
                continue
            
            # Generate ID
            ipo_id = f"ipo_{symbol or 'unknown'}_{datetime.utcnow().strftime('%Y%m%d')}"
            
            # Check if exists
            existing = StockOffer.query.filter_by(id=ipo_id).first()
            
            if existing:
                existing.symbol = symbol
                existing.company_name = company_name
                existing.exchange = ipo.get('exchange')
                existing.price_range = ipo.get('priceRange')
                existing.shares_offered = ipo.get('sharesOffered')
                existing.deal_type = ipo.get('dealType')
                existing.offer_price = ipo.get('offerPrice')
                updated += 1
            else:
                new_ipo = StockOffer(
                    id=ipo_id,
                    symbol=symbol,
                    company_name=company_name,
                    offer_type='ipo',
                    exchange=ipo.get('exchange'),
                    price_range=ipo.get('priceRange'),
                    shares_offered=ipo.get('sharesOffered'),
                    deal_type=ipo.get('dealType'),
                    offer_price=ipo.get('offerPrice'),
                    status='upcoming',
                )
                session.add(new_ipo)
                imported += 1
        except Exception as e:
            logger.error(f"Error importing IPO: {e}")
            errors += 1
    
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Error committing IPOs to database: {e}")
        return {'imported': 0, 'updated': 0, 'errors': len(ipos)}
    
    return {'imported': imported, 'updated': updated, 'errors': errors}
