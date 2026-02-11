"""
Floorsheet Handler
Real intraday trade data from yfinance for the most-active stocks.
Falls back to BulkTransaction database records.
"""
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

import yfinance as yf

from . import get_yfinance_session
from .screener_handler import get_most_active
from models.market import BulkTransaction

logger = logging.getLogger(__name__)

# Fallback tickers if screener returns nothing (blue-chip mix)
_FALLBACK_SYMBOLS = [
    'AAPL', 'MSFT', 'AMZN', 'GOOGL', 'TSLA',
    'META', 'NVDA', 'JPM', 'V', 'JNJ',
]

MAX_SYMBOLS = 10  # cap per request to avoid rate-limits


def get_floorsheet_from_db(
    symbol: Optional[str] = None,
    limit: int = 100,
) -> Optional[List[Dict[str, Any]]]:
    """
    Try to fetch recent bulk/block transactions from the database.
    Returns None if fewer than 5 records (treat as insufficient data).
    """
    try:
        query = BulkTransaction.query
        if symbol:
            query = query.filter(BulkTransaction.symbol == symbol.upper())
        records = (
            query
            .order_by(BulkTransaction.transaction_date.desc())
            .limit(limit)
            .all()
        )
        if records and len(records) >= 5:
            return [t.to_dict() for t in records]
    except Exception as e:
        logger.warning(f"Floorsheet DB query failed: {e}")
    return None


def _resolve_symbols(symbol_filter: Optional[str]) -> List[str]:
    """Determine which tickers to pull intraday data for."""
    if symbol_filter:
        return [symbol_filter.upper()]

    active = get_most_active(limit=MAX_SYMBOLS) or []
    symbols = [a['symbol'] for a in active if a.get('symbol')]
    return symbols[:MAX_SYMBOLS] if symbols else _FALLBACK_SYMBOLS[:MAX_SYMBOLS]


def _infer_side(open_price: float, close_price: float) -> str:
    """Infer trade side from bar direction."""
    return 'buy' if close_price >= open_price else 'sell'


def fetch_live_floorsheet(
    symbol: Optional[str] = None,
    limit: int = 100,
) -> Dict[str, Any]:
    """
    Fetch real 1-minute intraday bars from yfinance and format as trade records.

    Returns:
        Dict with 'trades' list, 'source', and 'timestamp'.
    """
    symbols = _resolve_symbols(symbol)
    session = get_yfinance_session()
    trades: List[Dict[str, Any]] = []

    for sym in symbols:
        try:
            ticker = yf.Ticker(sym, session=session)
            hist = ticker.history(period='1d', interval='1m')
            if hist is None or hist.empty:
                continue

            for ts, row in hist.iterrows():
                close_price = float(row['Close']) if row['Close'] else None
                open_price = float(row['Open']) if row['Open'] else None
                volume = int(row['Volume']) if row['Volume'] else 0

                if close_price is None or volume == 0:
                    continue

                trades.append({
                    'id': f"{sym}-{ts.isoformat()}",
                    'symbol': sym,
                    'transactionDate': ts.isoformat(),
                    'price': round(close_price, 4),
                    'quantity': volume,
                    'amount': round(close_price * volume, 2),
                    'side': _infer_side(open_price or 0, close_price),
                    'open': round(open_price, 4) if open_price else None,
                    'high': round(float(row['High']), 4) if row['High'] else None,
                    'low': round(float(row['Low']), 4) if row['Low'] else None,
                })
        except Exception as e:
            logger.warning(f"Floorsheet: error fetching {sym}: {e}")
            continue

    # Most recent first
    trades.sort(key=lambda t: t['transactionDate'], reverse=True)

    return {
        'trades': trades[:limit],
        'source': 'live',
        'timestamp': datetime.utcnow().isoformat(),
    }
