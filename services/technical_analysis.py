"""
Technical Analysis Service
Calculates indicators and generates buy/sell signals for Risk Analyzer
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

def calculate_rsi(data: pd.Series, period: int = 14) -> pd.Series:
    """Calculate Relative Strength Index"""
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).fillna(0)
    loss = (-delta.where(delta < 0, 0)).fillna(0)

    avg_gain = gain.rolling(window=period, min_periods=1).mean()
    avg_loss = loss.rolling(window=period, min_periods=1).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_sma(data: pd.Series, period: int) -> pd.Series:
    """Calculate Simple Moving Average"""
    return data.rolling(window=period).mean()

def calculate_ema(data: pd.Series, period: int) -> pd.Series:
    """Calculate Exponential Moving Average"""
    return data.ewm(span=period, adjust=False).mean()

def calculate_macd(data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    """Calculate MACD"""
    exp1 = data.ewm(span=fast, adjust=False).mean()
    exp2 = data.ewm(span=slow, adjust=False).mean()
    macd_line = exp1 - exp2
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram

def calculate_stochastic(high: pd.Series, low: pd.Series, close: pd.Series, k_period: int = 14, d_period: int = 3):
    """Calculate Stochastic Oscillator"""
    lowest_low = low.rolling(window=k_period).min()
    highest_high = high.rolling(window=k_period).max()
    
    k = 100 * ((close - lowest_low) / (highest_high - lowest_low))
    d = k.rolling(window=d_period).mean()
    return k, d

def get_signal_label(score: int) -> str:
    """Convert numerical score to text label"""
    if score >= 6: return "Strong Buy"
    if score >= 2: return "Buy"
    if score <= -6: return "Strong Sell"
    if score <= -2: return "Sell"
    return "Neutral"

def analyze_stock(symbol: str, history_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze stock data and return technical indicators with summary.
    
    Args:
        symbol: Stock symbol
        history_data: List of dicts with keys: date, open, high, low, close, volume (Expected chronologically sorted)
    """
    if not history_data or len(history_data) < 50:
        return {
            'symbol': symbol,
            'status': 'error',
            'message': 'Insufficient data for analysis'
        }

    try:
        df = pd.DataFrame(history_data)
        
        # Ensure correct types
        df['close'] = pd.to_numeric(df['close'])
        df['high'] = pd.to_numeric(df['high'])
        df['low'] = pd.to_numeric(df['low'])
        
        current_price = df['close'].iloc[-1]
        
        # --- Oscillators ---
        # RSI 14
        df['rsi_14'] = calculate_rsi(df['close'], 14)
        current_rsi = df['rsi_14'].iloc[-1]
        
        # Stochastic
        df['stoch_k'], df['stoch_d'] = calculate_stochastic(df['high'], df['low'], df['close'])
        current_stoch_k = df['stoch_k'].iloc[-1]
        
        # MACD
        df['macd'], df['macd_signal'], _ = calculate_macd(df['close'])
        current_macd = df['macd'].iloc[-1]
        current_macd_signal = df['macd_signal'].iloc[-1]
        
        # Commodity Channel Index (CCI) - Simplified calculation
        # CCI = (Typical Price - MA) / (0.015 * Mean Deviation)
        tp = (df['high'] + df['low'] + df['close']) / 3
        cci_ma = tp.rolling(window=20).mean()
        mean_dev = tp.rolling(window=20).apply(lambda x: np.mean(np.abs(x - np.mean(x))))
        df['cci'] = (tp - cci_ma) / (0.015 * mean_dev)
        current_cci = df['cci'].iloc[-1]

        # --- Moving Averages ---
        ma_periods = [10, 20, 50, 100, 200]
        ma_values = {}
        for p in ma_periods:
            df[f'sma_{p}'] = calculate_sma(df['close'], p)
            df[f'ema_{p}'] = calculate_ema(df['close'], p)
            
            if len(df) >= p:
                ma_values[f'sma_{p}'] = df[f'sma_{p}'].iloc[-1]
                ma_values[f'ema_{p}'] = df[f'ema_{p}'].iloc[-1]
            else:
                ma_values[f'sma_{p}'] = None
                ma_values[f'ema_{p}'] = None

        # --- Signal Logic & Scoring ---
        # Score ranges from -10 to +10 (roughly)
        score = 0
        oscillator_score = 0
        ma_score = 0
        
        summary_details = {
            'oscillators': {'buy': 0, 'sell': 0, 'neutral': 0},
            'movingAverages': {'buy': 0, 'sell': 0, 'neutral': 0}
        }
        
        # RSI Logic
        rsi_signal = "Neutral"
        if current_rsi < 30: 
            score += 1; oscillator_score += 1; rsi_signal = "Buy"; summary_details['oscillators']['buy'] += 1
        elif current_rsi > 70: 
            score -= 1; oscillator_score -= 1; rsi_signal = "Sell"; summary_details['oscillators']['sell'] += 1
        else:
            summary_details['oscillators']['neutral'] += 1
            
        # Stochastic Logic
        stoch_signal = "Neutral"
        if current_stoch_k < 20: 
            score += 1; oscillator_score += 1; stoch_signal = "Buy"; summary_details['oscillators']['buy'] += 1
        elif current_stoch_k > 80: 
            score -= 1; oscillator_score -= 1; stoch_signal = "Sell"; summary_details['oscillators']['sell'] += 1
        else:
            summary_details['oscillators']['neutral'] += 1

        # MACD Logic
        macd_diff = current_macd - current_macd_signal
        macd_signal_text = "Neutral"
        if macd_diff > 0: 
            score += 1; oscillator_score += 1; macd_signal_text = "Buy"; summary_details['oscillators']['buy'] += 1
        elif macd_diff < 0: 
            score -= 1; oscillator_score -= 1; macd_signal_text = "Sell"; summary_details['oscillators']['sell'] += 1
        else:
             summary_details['oscillators']['neutral'] += 1

        # CCI Logic
        cci_label = "Neutral"
        if current_cci < -100:
             score += 1; oscillator_score += 1; cci_label = "Buy"; summary_details['oscillators']['buy'] += 1
        elif current_cci > 100:
             score -= 1; oscillator_score -= 1; cci_label = "Sell"; summary_details['oscillators']['sell'] += 1
        else:
             summary_details['oscillators']['neutral'] += 1


        # MA Logic (Price vs SMA/EMA)
        # We check Price vs SMA20, SMA50, SMA200
        # Price > SMA = Bullish (Buy)
        
        ma_checks = [20, 50, 200]
        ma_details = []
        
        for p in ma_checks:
            sma_val = ma_values.get(f'sma_{p}')
            if sma_val:
                if current_price > sma_val:
                    score += 1; ma_score += 1; summary_details['movingAverages']['buy'] += 1
                    ma_details.append({'name': f'SMA {p}', 'value': sma_val, 'signal': 'Buy'})
                else:
                    score -= 1; ma_score -= 1; summary_details['movingAverages']['sell'] += 1
                    ma_details.append({'name': f'SMA {p}', 'value': sma_val, 'signal': 'Sell'})
                    
        # EMA Crossovers (Golden Cross / Death Cross - Simplified to Price > EMA)
        for p in [10, 50]:
            ema_val = ma_values.get(f'ema_{p}')
            if ema_val:
                 if current_price > ema_val:
                     score += 0.5; ma_score += 0.5; summary_details['movingAverages']['buy'] += 1
                 else:
                     score -= 0.5; ma_score -= 0.5; summary_details['movingAverages']['sell'] += 1

        # Final Summary
        summary_text = get_signal_label(score)
        
        return {
            'symbol': symbol,
            'price': current_price,
            'summary': {
                'score': score, # approx range -10 to 10
                'signal': summary_text,
                'oscillatorsScore': oscillator_score,
                'movingAveragesScore': ma_score,
                'counts': summary_details
            },
            'indicators': {
                'rsi': {'value': current_rsi, 'signal': rsi_signal},
                'stoch': {'k': current_stoch_k, 'signal': stoch_signal},
                'macd': {'value': current_macd, 'signal': macd_signal_text},
                'cci': {'value': current_cci, 'signal': cci_label},
                'movingAverages': ma_details
            }
        }

    except Exception as e:
        logger.error(f"Error analyzing stock {symbol}: {e}")
        return {
            'symbol': symbol,
            'status': 'error',
            'message': str(e)
        }
