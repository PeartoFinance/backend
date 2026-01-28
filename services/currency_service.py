"""
Currency Service
Handles stateless currency conversion logic using real-time rates.
"""
from models import db, ForexRate
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

def convert_usd_to_target(amount_usd, target_currency):
    """
    Converts a USD amount to a target currency for display purposes.
    
    Args:
        amount_usd: The value in USD (float or Decimal)
        target_currency: The 3-letter currency code (e.g., 'EUR', 'NPR')
        
    Returns:
        Dictionary with conversion results or error
    """
    try:
        target_currency = target_currency.upper()
        
        # 1. Handle USD to USD (no conversion needed)
        if target_currency == 'USD':
            return {
                'original_amount': float(amount_usd),
                'converted_amount': float(amount_usd),
                'rate': 1.0,
                'currency': 'USD',
                'status': 'success'
            }

        # 2. Fetch the latest rate from our database
        # This table is updated by our background cron job
        rate_record = ForexRate.query.filter_by(
            base_currency='USD',
            target_currency=target_currency
        ).first()

        if not rate_record or not rate_record.rate:
            # If rate is missing, try to fetch it on-the-fly from Yahoo Finance
            from handlers.market_data.forex_handler import get_forex_quote
            
            logger.info(f"Rate for {target_currency} missing. Fetching on-demand...")
            symbol = f"USD{target_currency}=X"
            quote = get_forex_quote(symbol)
            
            if quote and quote.get('price'):
                # Save it to DB so the cron job picks it up later
                rate_record = ForexRate(
                    base_currency='USD',
                    target_currency=target_currency,
                    rate=quote.get('price'),
                    change=quote.get('change'),
                    change_percent=quote.get('changePercent'),
                    high=quote.get('high'),
                    low=quote.get('low')
                )
                db.session.add(rate_record)
                db.session.commit()
            else:
                return {
                    'status': 'error',
                    'message': f'Exchange rate for {target_currency} could not be found.'
                }

        # 3. Perform the conversion
        rate = Decimal(str(rate_record.rate))
        usd_val = Decimal(str(amount_usd))
        converted_val = usd_val * rate

        return {
            'original_amount_usd': float(usd_val),
            'converted_amount': round(float(converted_val), 2),
            'rate': float(rate),
            'currency': target_currency,
            'last_updated': rate_record.last_updated.isoformat() if rate_record.last_updated else None,
            'status': 'success'
        }

    except Exception as e:
        logger.error(f"Currency conversion error: {e}")
        return {
            'status': 'error',
            'message': str(e)
        }

def get_all_available_rates():
    """
    Returns a list of all available currency rates in the system.
    """
    rates = ForexRate.query.all()
    return [r.to_dict() for r in rates]
