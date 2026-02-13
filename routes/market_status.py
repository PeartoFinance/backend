"""
Market Status Routes
Dynamic market open/close status based on user's country
"""
from flask import Blueprint, jsonify, request
from datetime import datetime
import pytz
from extensions import cache

market_status_bp = Blueprint('market_status', __name__)


def get_market_status_for_exchange(exchange):
    """Calculate if market is currently open based on exchange hours and timezone"""
    try:
        # Get exchange timezone from database
        tz = pytz.timezone(exchange.timezone)
        now = datetime.now(tz)
        
        # Check if today is a trading day
        trading_days = exchange.trading_days.split(',') if exchange.trading_days else ['MON', 'TUE', 'WED', 'THU', 'FRI']
        day_map = {0: 'MON', 1: 'TUE', 2: 'WED', 3: 'THU', 4: 'FRI', 5: 'SAT', 6: 'SUN'}
        today = day_map[now.weekday()]
        
        if today not in trading_days:
            # Find next trading day
            next_day_idx = (now.weekday() + 1) % 7
            for _ in range(7):
                if day_map[next_day_idx] in trading_days:
                    break
                next_day_idx = (next_day_idx + 1) % 7
            return {
                'isOpen': False,
                'reason': 'weekend',
                'message': f'Opens {day_map[next_day_idx]} {exchange.open_time}',
                'shortMessage': 'Closed',
                'nextOpenDay': day_map[next_day_idx]
            }
        
        # Parse open/close times
        open_parts = exchange.open_time.split(':')
        close_parts = exchange.close_time.split(':')
        
        open_time = now.replace(hour=int(open_parts[0]), minute=int(open_parts[1]), second=0, microsecond=0)
        close_time = now.replace(hour=int(close_parts[0]), minute=int(close_parts[1]), second=0, microsecond=0)
        
        if now < open_time:
            # Before market open
            time_until_open = open_time - now
            hours, remainder = divmod(int(time_until_open.total_seconds()), 3600)
            minutes = remainder // 60
            return {
                'isOpen': False,
                'reason': 'pre_market',
                'message': f'Opens at {exchange.open_time}',
                'shortMessage': f'Opens {hours}h {minutes}m',
                'opensAt': exchange.open_time
            }
        elif now > close_time:
            # After market close - opens tomorrow (or next trading day)
            next_day_idx = (now.weekday() + 1) % 7
            for _ in range(7):
                if day_map[next_day_idx] in trading_days:
                    break
                next_day_idx = (next_day_idx + 1) % 7
            
            if next_day_idx == (now.weekday() + 1) % 7:
                next_open = f'tomorrow {exchange.open_time}'
            else:
                next_open = f'{day_map[next_day_idx]} {exchange.open_time}'
            
            return {
                'isOpen': False,
                'reason': 'after_hours',
                'message': f'Opens {next_open}',
                'shortMessage': 'Closed',
                'closedAt': exchange.close_time
            }
        else:
            # Market is open
            time_until_close = close_time - now
            hours, remainder = divmod(int(time_until_close.total_seconds()), 3600)
            minutes = remainder // 60
            return {
                'isOpen': True,
                'reason': 'trading',
                'message': f'Closes at {exchange.close_time}',
                'shortMessage': f'Closes {hours}h {minutes}m',
                'closesAt': exchange.close_time
            }
    except Exception as e:
        return {
            'isOpen': False,
            'reason': 'error',
            'message': 'Unable to determine market status',
            'error': str(e)
        }


@market_status_bp.route('/status', methods=['GET'])
@cache.cached(timeout=60, query_string=True)
def get_market_status():
    """
    Get market status for user's country.
    Uses X-User-Country header or defaults to US.
    
    Headers:
        X-User-Country: US (2-letter country code)
        
    Returns:
        {
            "exchange": { ... exchange info ... },
            "status": { isOpen, message, ... },
            "localTime": "2024-01-21 09:45:00",
            "exchangeTime": "2024-01-21 09:45:00 ET"
        }
    """
    from models import MarketHours
    
    # Get user's country from header, default to US
    country_code = request.headers.get('X-User-Country', 'US').upper()
    
    # Find primary exchange for this country
    exchange = MarketHours.query.filter_by(
        country_code=country_code,
        is_primary=True,
        is_active=True
    ).first()
    
    # Fallback to any exchange for this country
    if not exchange:
        exchange = MarketHours.query.filter_by(
            country_code=country_code,
            is_active=True
        ).first()
    
    # Fallback to US market if country not found
    if not exchange:
        exchange = MarketHours.query.filter_by(
            country_code='US',
            is_primary=True,
            is_active=True
        ).first()
    
    if not exchange:
        return jsonify({
            'exchange': None,
            'status': {
                'isOpen': False,
                'reason': 'no_data',
                'message': 'No market data available'
            }
        })
    
    # Get current time in exchange timezone (from database)
    try:
        tz = pytz.timezone(exchange.timezone)  # Use timezone from DB
        exchange_time = datetime.now(tz)
        exchange_time_str = exchange_time.strftime('%Y-%m-%d %H:%M:%S %Z')
        exchange_time_short = exchange_time.strftime('%H:%M %Z')
        
        # Also show what day it is in exchange timezone
        day_map = {0: 'MON', 1: 'TUE', 2: 'WED', 3: 'THU', 4: 'FRI', 5: 'SAT', 6: 'SUN'}
        current_day = day_map[exchange_time.weekday()]
    except Exception as e:
        exchange_time_str = None
        exchange_time_short = None
        current_day = None
    
    status = get_market_status_for_exchange(exchange)
    
    # Add current time info to status
    status['currentTime'] = exchange_time_short
    status['currentDay'] = current_day
    status['timezone'] = exchange.timezone
    
    return jsonify({
        'exchange': exchange.to_dict(),
        'status': status,
        'exchangeTime': exchange_time_str,
        'userCountry': country_code
    })


@market_status_bp.route('/exchanges', methods=['GET'])
@cache.cached(timeout=300, query_string=True)
def get_all_exchanges():
    """Get all active exchanges"""
    from models import MarketHours
    
    exchanges = MarketHours.query.filter_by(is_active=True).order_by(MarketHours.country_code).all()
    
    return jsonify({
        'exchanges': [e.to_dict() for e in exchanges],
        'count': len(exchanges)
    })


@market_status_bp.route('/seed', methods=['POST'])
def seed_market_hours():
    """Seed demo market hours data (admin only)"""
    from models import MarketHours, db
    
    # Check for admin token
    token = request.headers.get('X-Cron-Token') or request.args.get('token')
    import os
    if token != os.getenv('CRON_SECRET', 'your-cron-secret-key'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Demo data for major exchanges
    exchanges_data = [
        # US Markets
        {
            'exchange_code': 'NYSE',
            'exchange_name': 'New York Stock Exchange',
            'country_code': 'US',
            'open_time': '09:30',
            'close_time': '16:00',
            'timezone': 'America/New_York',
            'trading_days': 'MON,TUE,WED,THU,FRI',
            'is_primary': True
        },
        {
            'exchange_code': 'NASDAQ',
            'exchange_name': 'NASDAQ',
            'country_code': 'US',
            'open_time': '09:30',
            'close_time': '16:00',
            'timezone': 'America/New_York',
            'trading_days': 'MON,TUE,WED,THU,FRI',
            'is_primary': False
        },
        # UK Market
        {
            'exchange_code': 'LSE',
            'exchange_name': 'London Stock Exchange',
            'country_code': 'GB',
            'open_time': '08:00',
            'close_time': '16:30',
            'timezone': 'Europe/London',
            'trading_days': 'MON,TUE,WED,THU,FRI',
            'is_primary': True
        },
        # Japan Market
        {
            'exchange_code': 'TSE',
            'exchange_name': 'Tokyo Stock Exchange',
            'country_code': 'JP',
            'open_time': '09:00',
            'close_time': '15:00',
            'timezone': 'Asia/Tokyo',
            'trading_days': 'MON,TUE,WED,THU,FRI',
            'is_primary': True
        },
        # India Market
        {
            'exchange_code': 'NSE',
            'exchange_name': 'National Stock Exchange of India',
            'country_code': 'IN',
            'open_time': '09:15',
            'close_time': '15:30',
            'timezone': 'Asia/Kolkata',
            'trading_days': 'MON,TUE,WED,THU,FRI',
            'is_primary': True
        },
        {
            'exchange_code': 'BSE',
            'exchange_name': 'Bombay Stock Exchange',
            'country_code': 'IN',
            'open_time': '09:15',
            'close_time': '15:30',
            'timezone': 'Asia/Kolkata',
            'trading_days': 'MON,TUE,WED,THU,FRI',
            'is_primary': False
        },
        # Nepal Market
        {
            'exchange_code': 'NEPSE',
            'exchange_name': 'Nepal Stock Exchange',
            'country_code': 'NP',
            'open_time': '11:00',
            'close_time': '15:00',
            'timezone': 'Asia/Kathmandu',
            'trading_days': 'SUN,MON,TUE,WED,THU',
            'is_primary': True
        },
        # Hong Kong Market
        {
            'exchange_code': 'HKEX',
            'exchange_name': 'Hong Kong Stock Exchange',
            'country_code': 'HK',
            'open_time': '09:30',
            'close_time': '16:00',
            'timezone': 'Asia/Hong_Kong',
            'trading_days': 'MON,TUE,WED,THU,FRI',
            'is_primary': True
        },
        # Germany Market
        {
            'exchange_code': 'FRA',
            'exchange_name': 'Frankfurt Stock Exchange',
            'country_code': 'DE',
            'open_time': '09:00',
            'close_time': '17:30',
            'timezone': 'Europe/Berlin',
            'trading_days': 'MON,TUE,WED,THU,FRI',
            'is_primary': True
        },
        # Australia Market
        {
            'exchange_code': 'ASX',
            'exchange_name': 'Australian Securities Exchange',
            'country_code': 'AU',
            'open_time': '10:00',
            'close_time': '16:00',
            'timezone': 'Australia/Sydney',
            'trading_days': 'MON,TUE,WED,THU,FRI',
            'is_primary': True
        },
    ]
    
    seeded = 0
    for data in exchanges_data:
        # Check if already exists
        existing = MarketHours.query.filter_by(exchange_code=data['exchange_code']).first()
        if not existing:
            exchange = MarketHours(**data)
            db.session.add(exchange)
            seeded += 1
    
    db.session.commit()
    
    return jsonify({
        'ok': True,
        'message': f'Seeded {seeded} exchanges',
        'total': len(exchanges_data)
    })
