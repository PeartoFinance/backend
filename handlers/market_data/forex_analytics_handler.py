"""
Forex Analytics Handler
Real-data currency strength index and cross-pair correlation matrix.
Uses numpy for efficient computation.
"""
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

import numpy as np

from .forex_handler import get_forex_quote, get_forex_history, COMMON_CURRENCIES
from .rate_limiter import check_rate_limit
from models import ForexRate

logger = logging.getLogger(__name__)

# Major currencies for strength / correlation analysis
MAJOR_CURRENCIES = ['USD', 'EUR', 'GBP', 'JPY', 'CHF', 'AUD', 'CAD', 'NZD']

# yfinance symbols for all cross-pair combinations
CROSS_PAIRS: Dict[Tuple[str, str], str] = {
    ('USD', 'EUR'): 'USDEUR=X', ('USD', 'GBP'): 'USDGBP=X',
    ('USD', 'JPY'): 'USDJPY=X', ('USD', 'CHF'): 'USDCHF=X',
    ('USD', 'AUD'): 'USDAUD=X', ('USD', 'CAD'): 'USDCAD=X',
    ('USD', 'NZD'): 'USDNZD=X',
    ('EUR', 'GBP'): 'EURGBP=X', ('EUR', 'JPY'): 'EURJPY=X',
    ('EUR', 'CHF'): 'EURCHF=X', ('EUR', 'AUD'): 'EURAUD=X',
    ('EUR', 'CAD'): 'EURCAD=X', ('EUR', 'NZD'): 'EURNZD=X',
    ('GBP', 'JPY'): 'GBPJPY=X', ('GBP', 'CHF'): 'GBPCHF=X',
    ('GBP', 'AUD'): 'GBPAUD=X', ('GBP', 'CAD'): 'GBPCAD=X',
    ('GBP', 'NZD'): 'GBPNZD=X',
    ('AUD', 'JPY'): 'AUDJPY=X', ('AUD', 'CHF'): 'AUDCHF=X',
    ('AUD', 'CAD'): 'AUDCAD=X', ('AUD', 'NZD'): 'AUDNZD=X',
    ('CAD', 'JPY'): 'CADJPY=X', ('CAD', 'CHF'): 'CADCHF=X',
    ('CHF', 'JPY'): 'CHFJPY=X',
    ('NZD', 'JPY'): 'NZDJPY=X', ('NZD', 'CHF'): 'NZDCHF=X',
    ('NZD', 'CAD'): 'NZDCAD=X',
}


def _collect_pair_changes() -> Dict[Tuple[str, str], float]:
    """
    Gather daily change-percent for every available currency pair.
    Priority: DB (fast, cron-cached) → live yfinance for gaps.
    """
    pair_changes: Dict[Tuple[str, str], float] = {}

    # 1. DB rates (fast path)
    try:
        for r in ForexRate.query.all():
            if r.change_percent is not None:
                pair_changes[(r.base_currency, r.target_currency)] = float(r.change_percent)
    except Exception as e:
        logger.warning(f"Failed to read ForexRate from DB: {e}")

    # 2. Fill in missing cross-pairs from live yfinance
    for (base, quote), yf_symbol in CROSS_PAIRS.items():
        if (base, quote) in pair_changes:
            continue
        if not check_rate_limit():
            break
        try:
            q = get_forex_quote(yf_symbol)
            if q and q.get('changePercent') is not None:
                pair_changes[(base, quote)] = float(q['changePercent'])
        except Exception:
            continue

    return pair_changes


def compute_currency_strength() -> Dict[str, Any]:
    """
    Currency Strength Index.
    Aggregates cross-pair performance per currency and normalises to 0-100.

    Convention: for pair BASE/QUOTE, a positive changePercent means
    the rate went up → BASE weakened, QUOTE strengthened.
    """
    pair_changes = _collect_pair_changes()

    # Accumulate per-currency scores
    scores: Dict[str, List[float]] = {c: [] for c in MAJOR_CURRENCIES}
    for (base, quote), chg in pair_changes.items():
        if chg is None:
            continue
        if base in scores:
            scores[base].append(-chg)   # base weakened when rate rises
        if quote in scores:
            scores[quote].append(chg)   # quote strengthened when rate rises

    # Mean score per currency
    raw = {c: float(np.mean(s)) if s else 0.0 for c, s in scores.items()}

    # Normalise to 0-100
    vals = np.array(list(raw.values()))
    lo, hi = float(vals.min()), float(vals.max())
    spread = hi - lo if hi != lo else 1.0
    normalised = {c: round(((v - lo) / spread) * 100, 1) for c, v in raw.items()}

    # Rank descending
    ranked = sorted(normalised.items(), key=lambda x: x[1], reverse=True)

    return {
        'currencies': [
            {
                'currency': curr,
                'strength': score,
                'rank': rank,
                'avgChangePercent': round(raw[curr], 4),
                'pairCount': len(scores[curr]),
            }
            for rank, (curr, score) in enumerate(ranked, 1)
        ],
        'timestamp': datetime.utcnow().isoformat(),
    }


def compute_correlation_matrix(
    period: str = '1mo',
    interval: str = '1d',
) -> Dict[str, Any]:
    """
    Cross-pair Pearson correlation matrix from real historical close prices.

    Uses numpy.corrcoef for efficient matrix computation.
    """
    # Build USD-based pair list
    pair_labels = [f'USD/{c}' for c in MAJOR_CURRENCIES if c != 'USD']
    pair_symbols = [f'USD{c}' for c in MAJOR_CURRENCIES if c != 'USD']

    # Fetch historical close prices per pair
    histories: Dict[str, List[float]] = {}
    for label, symbol in zip(pair_labels, pair_symbols):
        try:
            hist = get_forex_history(symbol, period=period, interval=interval)
            if hist:
                closes = [h['close'] for h in hist if h.get('close') is not None]
                if len(closes) >= 5:  # need minimum data points
                    histories[label] = closes
        except Exception:
            continue

    labels = list(histories.keys())
    if len(labels) < 2:
        return {
            'labels': labels,
            'matrix': [[1.0]] if labels else [],
            'period': period,
            'interval': interval,
            'timestamp': datetime.utcnow().isoformat(),
        }

    # Align lengths (trim to shortest series)
    min_len = min(len(v) for v in histories.values())
    data = np.array([histories[lbl][:min_len] for lbl in labels], dtype=np.float64)

    # Compute full correlation matrix via numpy
    corr = np.corrcoef(data)
    # Replace any NaN with 0
    corr = np.nan_to_num(corr, nan=0.0)
    matrix = [[round(float(corr[i][j]), 4) for j in range(len(labels))] for i in range(len(labels))]

    return {
        'labels': labels,
        'matrix': matrix,
        'period': period,
        'interval': interval,
        'timestamp': datetime.utcnow().isoformat(),
    }
