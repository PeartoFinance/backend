"""
AI Tools - Tool definitions and executors for AI chat
Enhanced with comparison, screening, technical analysis, and portfolio tools
"""
import re
import json
import math
from typing import Dict, Any, List, Optional
from models.base import db


# Tool definitions for OpenAI function calling format
AI_TOOLS = [
    {
        "name": "get_stock_quote",
        "description": "Get real-time stock price and detailed information for a given symbol",
        "parameters": {
            "symbol": {"type": "string", "description": "Stock ticker symbol (e.g., AAPL, MSFT, TSLA)"}
        }
    },
    {
        "name": "get_crypto_price",
        "description": "Get cryptocurrency price and market data",
        "parameters": {
            "symbol": {"type": "string", "description": "Crypto symbol (e.g., BTC, ETH, SOL)"}
        }
    },
    {
        "name": "get_market_movers",
        "description": "Get top gaining or losing stocks for the day",
        "parameters": {
            "type": {"type": "string", "enum": ["gainers", "losers"], "description": "Type of movers"},
            "limit": {"type": "number", "description": "Number of results (default 5)"}
        }
    },
    {
        "name": "compare_stocks",
        "description": "Compare two or more stocks/crypto side by side with key metrics",
        "parameters": {
            "symbols": {"type": "array", "description": "List of 2-5 ticker symbols to compare (e.g., ['AAPL','MSFT'])"}
        }
    },
    {
        "name": "screen_stocks",
        "description": "Screen/filter stocks by criteria like sector, market cap, P/E ratio, dividend yield",
        "parameters": {
            "sector": {"type": "string", "description": "Filter by sector (e.g., Technology, Healthcare)"},
            "min_market_cap": {"type": "number", "description": "Minimum market cap in billions"},
            "max_pe": {"type": "number", "description": "Maximum P/E ratio"},
            "min_dividend_yield": {"type": "number", "description": "Minimum dividend yield %"},
            "sort_by": {"type": "string", "description": "Sort by: market_cap, change_percent, pe_ratio, dividend_yield"},
            "limit": {"type": "number", "description": "Max results (default 10)"}
        }
    },
    {
        "name": "get_sector_performance",
        "description": "Get performance overview of market sectors",
        "parameters": {}
    },
    {
        "name": "get_technical_indicators",
        "description": "Get technical analysis indicators for a stock (RSI, moving averages, support/resistance)",
        "parameters": {
            "symbol": {"type": "string", "description": "Stock ticker symbol"}
        }
    },
    {
        "name": "calculate_sip",
        "description": "Calculate SIP (Systematic Investment Plan) returns",
        "parameters": {
            "monthly_amount": {"type": "number", "description": "Monthly investment amount"},
            "years": {"type": "number", "description": "Investment duration in years"},
            "expected_return": {"type": "number", "description": "Expected annual return percentage"}
        }
    },
    {
        "name": "calculate_emi",
        "description": "Calculate EMI (Equated Monthly Installment) for a loan",
        "parameters": {
            "principal": {"type": "number", "description": "Loan principal amount"},
            "interest_rate": {"type": "number", "description": "Annual interest rate percentage"},
            "tenure_months": {"type": "number", "description": "Loan tenure in months"}
        }
    },
    {
        "name": "calculate_compound_interest",
        "description": "Calculate compound interest on a lump sum investment",
        "parameters": {
            "principal": {"type": "number", "description": "Initial investment amount"},
            "rate": {"type": "number", "description": "Annual interest rate percentage"},
            "years": {"type": "number", "description": "Number of years"},
            "compounds_per_year": {"type": "number", "description": "Compounding frequency per year (e.g., 12 for monthly, 4 for quarterly)"}
        }
    },
    {
        "name": "get_forex_rates",
        "description": "Get forex exchange rates for a base currency",
        "parameters": {
            "base": {"type": "string", "description": "Base currency (e.g., USD)"}
        }
    },
    {
        "name": "get_weather",
        "description": "Get weather information for a location",
        "parameters": {
            "location": {"type": "string", "description": "City name"}
        }
    },
    {
        "name": "search_news",
        "description": "Search for financial news articles",
        "parameters": {
            "query": {"type": "string", "description": "Search query"},
            "limit": {"type": "number", "description": "Number of results (default 5)"}
        }
    }
]


def get_all_tools() -> List[Dict]:
    """Get all available tools"""
    return AI_TOOLS


async def execute_tool(tool_name: str, args: Dict, context: Dict = None) -> Dict[str, Any]:
    """Execute a tool and return result"""
    context = context or {}
    
    try:
        if tool_name == 'get_stock_quote':
            return await get_stock_quote(args.get('symbol', ''))
        elif tool_name == 'get_crypto_price':
            return await get_crypto_price(args.get('symbol', ''))
        elif tool_name == 'get_market_movers':
            return await get_market_movers(args.get('type', 'gainers'), args.get('limit', 5))
        elif tool_name == 'compare_stocks':
            return await compare_stocks(args.get('symbols', []))
        elif tool_name == 'screen_stocks':
            return await screen_stocks(args)
        elif tool_name == 'get_sector_performance':
            return await get_sector_performance()
        elif tool_name == 'get_technical_indicators':
            return await get_technical_indicators(args.get('symbol', ''))
        elif tool_name == 'calculate_sip':
            return calculate_sip(
                args.get('monthly_amount', args.get('monthlyAmount', 0)),
                args.get('years', 0),
                args.get('expected_return', args.get('expectedReturn', 12))
            )
        elif tool_name == 'calculate_emi':
            return calculate_emi(
                args.get('principal', 0),
                args.get('interest_rate', args.get('interestRate', 10)),
                args.get('tenure_months', args.get('tenureMonths', 12))
            )
        elif tool_name == 'calculate_compound_interest':
            return calculate_compound_interest(
                args.get('principal', 0),
                args.get('rate', 0),
                args.get('years', 0),
                args.get('compounds_per_year', args.get('compoundsPerYear', 12))
            )
        elif tool_name == 'get_forex_rates':
            return await get_forex_rates(args.get('base', 'USD'))
        elif tool_name == 'get_weather':
            return await get_weather(args.get('location', 'Kathmandu'))
        elif tool_name == 'search_news':
            return await search_news(args.get('query', ''), args.get('limit', 5))
        else:
            return {"error": f"Unknown tool: {tool_name}"}
    except Exception as e:
        return {"error": str(e)}


# Tool Implementations

async def get_stock_quote(symbol: str) -> Dict:
    """Get detailed stock quote from database"""
    from models import MarketData
    
    stock = MarketData.query.filter(
        MarketData.symbol == symbol.upper(),
        MarketData.asset_type == 'stock'
    ).first()
    
    if not stock:
        return {"error": f"Stock {symbol} not found"}
    
    result = {
        "symbol": stock.symbol,
        "name": stock.name,
        "price": float(stock.price) if stock.price else 0,
        "change": float(stock.change) if stock.change else 0,
        "changePercent": float(stock.change_percent) if stock.change_percent else 0,
        "volume": stock.volume,
        "marketCap": stock.market_cap,
        "source": "database"
    }
    
    # Add extended data if available
    if stock.pe_ratio:
        result["peRatio"] = float(stock.pe_ratio)
    if stock.eps:
        result["eps"] = float(stock.eps)
    if stock.dividend_yield:
        result["dividendYield"] = float(stock.dividend_yield)
    if stock.sector:
        result["sector"] = stock.sector
    if stock.industry:
        result["industry"] = stock.industry
    if stock._52_week_high:
        result["weekHigh52"] = float(stock._52_week_high)
    if stock._52_week_low:
        result["weekLow52"] = float(stock._52_week_low)
    if stock.beta:
        result["beta"] = float(stock.beta)
    if stock.day_high:
        result["dayHigh"] = float(stock.day_high)
    if stock.day_low:
        result["dayLow"] = float(stock.day_low)
    if stock.open_price:
        result["open"] = float(stock.open_price)
    if stock.previous_close:
        result["previousClose"] = float(stock.previous_close)
    
    return result


async def get_crypto_price(symbol: str) -> Dict:
    """Get crypto price from database"""
    from models import MarketData
    
    crypto = MarketData.query.filter(
        MarketData.symbol == symbol.upper(),
        MarketData.asset_type == 'crypto'
    ).first()
    
    if not crypto:
        return {"error": f"Crypto {symbol} not found"}
    
    return {
        "symbol": crypto.symbol,
        "name": crypto.name,
        "price": float(crypto.price) if crypto.price else 0,
        "change24h": float(crypto.change) if crypto.change else 0,
        "changePercent24h": float(crypto.change_percent) if crypto.change_percent else 0,
        "volume24h": crypto.volume,
        "marketCap": crypto.market_cap,
        "source": "database"
    }


async def get_market_movers(mover_type: str, limit: int = 5) -> Dict:
    """Get top gainers or losers"""
    from models import MarketData
    
    if mover_type == 'gainers':
        stocks = MarketData.query.filter(
            MarketData.asset_type == 'stock',
            MarketData.change_percent.isnot(None)
        ).order_by(MarketData.change_percent.desc()).limit(limit).all()
    else:
        stocks = MarketData.query.filter(
            MarketData.asset_type == 'stock',
            MarketData.change_percent.isnot(None)
        ).order_by(MarketData.change_percent.asc()).limit(limit).all()
    
    return {
        "type": mover_type,
        "movers": [{
            "symbol": s.symbol,
            "name": s.name,
            "price": float(s.price) if s.price else 0,
            "changePercent": float(s.change_percent) if s.change_percent else 0
        } for s in stocks]
    }


def calculate_sip(monthly_amount: float, years: int, expected_return: float) -> Dict:
    """Calculate SIP returns"""
    months = years * 12
    monthly_rate = expected_return / 12 / 100
    
    if monthly_rate == 0:
        future_value = monthly_amount * months
    else:
        future_value = monthly_amount * (((math.pow(1 + monthly_rate, months) - 1) / monthly_rate) * (1 + monthly_rate))
    
    total_invested = monthly_amount * months
    total_returns = future_value - total_invested
    
    return {
        "monthlyInvestment": monthly_amount,
        "duration": f"{years} years",
        "expectedReturn": f"{expected_return}%",
        "totalInvested": round(total_invested, 2),
        "estimatedReturns": round(total_returns, 2),
        "totalValue": round(future_value, 2)
    }


def calculate_emi(principal: float, interest_rate: float, tenure_months: int) -> Dict:
    """Calculate EMI for loan"""
    monthly_rate = interest_rate / 12 / 100
    
    if monthly_rate == 0:
        emi = principal / tenure_months
    else:
        emi = principal * monthly_rate * math.pow(1 + monthly_rate, tenure_months) / (math.pow(1 + monthly_rate, tenure_months) - 1)
    
    total_payment = emi * tenure_months
    total_interest = total_payment - principal
    
    return {
        "principal": principal,
        "interestRate": f"{interest_rate}%",
        "tenure": f"{tenure_months} months",
        "emi": round(emi, 2),
        "totalPayment": round(total_payment, 2),
        "totalInterest": round(total_interest, 2)
    }


async def get_forex_rates(base: str = 'USD') -> Dict:
    """Get forex rates"""
    from models import ForexRate
    
    rates = ForexRate.query.filter(
        ForexRate.base_currency == base.upper()
    ).limit(10).all()
    
    if not rates:
        # Return mock data
        return {
            "base": base,
            "rates": {
                "EUR": 0.92,
                "GBP": 0.79,
                "JPY": 149.50,
                "NPR": 133.25
            }
        }
    
    return {
        "base": base,
        "rates": {r.target_currency: float(r.rate) for r in rates}
    }


async def get_weather(location: str) -> Dict:
    """Get weather data"""
    # Mock weather data - could integrate with weather API
    import random
    return {
        "location": location,
        "temperature": random.randint(15, 35),
        "condition": random.choice(["Sunny", "Cloudy", "Partly Cloudy", "Clear"]),
        "humidity": random.randint(40, 80),
        "windSpeed": random.randint(5, 20)
    }


async def search_news(query: str, limit: int = 5) -> Dict:
    """Search news articles"""
    from models import News
    
    news = News.query.filter(
        News.title.ilike(f'%{query}%')
    ).order_by(News.published_at.desc()).limit(limit).all()
    
    if not news:
        return {
            "query": query,
            "message": "No news found. Check the News page for latest updates.",
            "results": []
        }
    
    return {
        "query": query,
        "results": [{
            "title": n.title,
            "summary": n.summary[:100] if n.summary else None,
            "source": n.source,
            "publishedAt": n.published_at.isoformat() if n.published_at else None
        } for n in news]
    }


# ─── NEW TOOLS ──────────────────────────────────────────────────

async def compare_stocks(symbols: list) -> Dict:
    """Compare multiple stocks side by side"""
    from models import MarketData
    
    if not symbols or len(symbols) < 2:
        return {"error": "Need at least 2 symbols to compare"}
    
    comparison = []
    for sym in symbols[:5]:
        stock = MarketData.query.filter(
            MarketData.symbol == sym.upper()
        ).first()
        
        if stock:
            entry = {
                "symbol": stock.symbol,
                "name": stock.name or stock.symbol,
                "price": float(stock.price) if stock.price else 0,
                "changePercent": float(stock.change_percent) if stock.change_percent else 0,
                "marketCap": stock.market_cap,
                "volume": stock.volume,
                "peRatio": float(stock.pe_ratio) if stock.pe_ratio else None,
                "eps": float(stock.eps) if stock.eps else None,
                "dividendYield": float(stock.dividend_yield) if stock.dividend_yield else None,
                "beta": float(stock.beta) if stock.beta else None,
                "sector": stock.sector,
                "weekHigh52": float(stock._52_week_high) if stock._52_week_high else None,
                "weekLow52": float(stock._52_week_low) if stock._52_week_low else None,
            }
            comparison.append(entry)
        else:
            comparison.append({"symbol": sym.upper(), "error": "Not found"})
    
    return {
        "type": "comparison",
        "stocks": comparison,
        "count": len(comparison)
    }


async def screen_stocks(criteria: Dict) -> Dict:
    """Screen stocks by various criteria"""
    from models import MarketData
    
    query = MarketData.query.filter(MarketData.asset_type == 'stock')
    
    sector = criteria.get('sector')
    if sector:
        query = query.filter(MarketData.sector.ilike(f'%{sector}%'))
    
    min_cap = criteria.get('min_market_cap')
    if min_cap:
        query = query.filter(MarketData.market_cap >= float(min_cap) * 1e9)
    
    max_pe = criteria.get('max_pe')
    if max_pe:
        query = query.filter(MarketData.pe_ratio <= float(max_pe), MarketData.pe_ratio > 0)
    
    min_div = criteria.get('min_dividend_yield')
    if min_div:
        query = query.filter(MarketData.dividend_yield >= float(min_div))
    
    # Sorting
    sort_by = criteria.get('sort_by', 'market_cap')
    sort_map = {
        'market_cap': MarketData.market_cap.desc(),
        'change_percent': MarketData.change_percent.desc(),
        'pe_ratio': MarketData.pe_ratio.asc(),
        'dividend_yield': MarketData.dividend_yield.desc(),
    }
    query = query.order_by(sort_map.get(sort_by, MarketData.market_cap.desc()))
    
    limit = min(int(criteria.get('limit', 10)), 20)
    stocks = query.limit(limit).all()
    
    return {
        "type": "screener",
        "criteria": {k: v for k, v in criteria.items() if v},
        "results": [{
            "symbol": s.symbol,
            "name": s.name,
            "price": float(s.price) if s.price else 0,
            "changePercent": float(s.change_percent) if s.change_percent else 0,
            "marketCap": s.market_cap,
            "peRatio": float(s.pe_ratio) if s.pe_ratio else None,
            "dividendYield": float(s.dividend_yield) if s.dividend_yield else None,
            "sector": s.sector,
        } for s in stocks],
        "count": len(stocks)
    }


async def get_sector_performance() -> Dict:
    """Get market sector performance overview"""
    from models import MarketData
    from sqlalchemy import func
    
    sectors = db.session.query(
        MarketData.sector,
        func.count(MarketData.id).label('count'),
        func.avg(MarketData.change_percent).label('avg_change'),
        func.sum(MarketData.market_cap).label('total_cap')
    ).filter(
        MarketData.asset_type == 'stock',
        MarketData.sector.isnot(None),
        MarketData.sector != ''
    ).group_by(MarketData.sector).order_by(
        func.avg(MarketData.change_percent).desc()
    ).limit(15).all()
    
    return {
        "type": "sector_performance",
        "sectors": [{
            "sector": s.sector,
            "stockCount": s.count,
            "avgChange": round(float(s.avg_change), 2) if s.avg_change else 0,
            "totalMarketCap": int(s.total_cap) if s.total_cap else 0,
        } for s in sectors]
    }


async def get_technical_indicators(symbol: str) -> Dict:
    """Get technical analysis indicators for a stock"""
    from models import MarketData
    
    stock = MarketData.query.filter(
        MarketData.symbol == symbol.upper(),
        MarketData.asset_type == 'stock'
    ).first()
    
    if not stock:
        return {"error": f"Stock {symbol} not found"}
    
    price = float(stock.price) if stock.price else 0
    high52 = float(stock._52_week_high) if stock._52_week_high else price * 1.15
    low52 = float(stock._52_week_low) if stock._52_week_low else price * 0.85
    day_high = float(stock.day_high) if stock.day_high else price * 1.01
    day_low = float(stock.day_low) if stock.day_low else price * 0.99
    prev_close = float(stock.previous_close) if stock.previous_close else price
    
    # Calculate derived indicators
    price_range_52w = high52 - low52
    position_in_range = ((price - low52) / price_range_52w * 100) if price_range_52w > 0 else 50
    
    # Simple RSI approximation from change percent
    change_pct = float(stock.change_percent) if stock.change_percent else 0
    rsi_approx = max(10, min(90, 50 + change_pct * 5))
    
    # Support/resistance levels  
    pivot = (day_high + day_low + price) / 3
    support1 = 2 * pivot - day_high
    resistance1 = 2 * pivot - day_low
    support2 = pivot - (day_high - day_low)
    resistance2 = pivot + (day_high - day_low)
    
    # Signal
    if rsi_approx > 70:
        signal = "Overbought"
    elif rsi_approx < 30:
        signal = "Oversold"
    elif change_pct > 2:
        signal = "Strong Bullish"
    elif change_pct > 0:
        signal = "Bullish"
    elif change_pct < -2:
        signal = "Strong Bearish"
    elif change_pct < 0:
        signal = "Bearish"
    else:
        signal = "Neutral"
    
    return {
        "type": "technical",
        "symbol": symbol.upper(),
        "price": price,
        "signal": signal,
        "rsi": round(rsi_approx, 1),
        "positionIn52wRange": round(position_in_range, 1),
        "support": [round(support2, 2), round(support1, 2)],
        "resistance": [round(resistance1, 2), round(resistance2, 2)],
        "pivot": round(pivot, 2),
        "weekHigh52": round(high52, 2),
        "weekLow52": round(low52, 2),
        "beta": float(stock.beta) if stock.beta else None,
    }


def calculate_compound_interest(principal: float, rate: float, years: int, compounds_per_year: int = 12) -> Dict:
    """Calculate compound interest"""
    if compounds_per_year <= 0:
        compounds_per_year = 12
    
    r = rate / 100
    n = compounds_per_year
    t = years
    
    final_amount = principal * math.pow(1 + r / n, n * t)
    total_interest = final_amount - principal
    
    # Year-by-year breakdown
    yearly = []
    for yr in range(1, min(years + 1, 31)):
        val = principal * math.pow(1 + r / n, n * yr)
        yearly.append({
            "year": yr,
            "value": round(val, 2),
            "interest": round(val - principal, 2)
        })
    
    return {
        "type": "compound_interest",
        "principal": principal,
        "rate": f"{rate}%",
        "years": years,
        "compoundingFrequency": {1: "Annually", 4: "Quarterly", 12: "Monthly", 365: "Daily"}.get(compounds_per_year, f"{compounds_per_year}x/year"),
        "finalAmount": round(final_amount, 2),
        "totalInterest": round(total_interest, 2),
        "effectiveRate": round((math.pow(1 + r / n, n) - 1) * 100, 2),
        "yearlyBreakdown": yearly[:10]  # First 10 years
    }


def parse_tool_calls(text: str) -> List[Dict]:
    """Parse tool calls from AI response"""
    tool_calls = []
    
    # Format: <tool_call>{"name": "...", "arguments": {...}}</tool_call>
    pattern = r'<tool_call>\s*([\s\S]*?)\s*</tool_call>'
    matches = re.findall(pattern, text, re.IGNORECASE)
    
    for match in matches:
        try:
            import json
            parsed = json.loads(match.strip())
            if 'name' in parsed:
                tool_calls.append({
                    "name": parsed['name'],
                    "arguments": parsed.get('arguments', parsed.get('args', {}))
                })
        except:
            pass
    
    # Format: ```json {...} ```
    code_pattern = r'```(?:json|tool)?\s*(\{[\s\S]*?\})\s*```'
    code_matches = re.findall(code_pattern, text, re.IGNORECASE)
    
    for match in code_matches:
        try:
            import json
            parsed = json.loads(match.strip())
            if 'name' in parsed and not any(tc['name'] == parsed['name'] for tc in tool_calls):
                tool_calls.append({
                    "name": parsed['name'],
                    "arguments": parsed.get('arguments', parsed.get('args', {}))
                })
        except:
            pass
    
    # Format: bare JSON {"name": "...", "arguments": {...}}
    bare_pattern = r'\{\s*"name"\s*:\s*"[^"]+"\s*,\s*"arguments"\s*:\s*\{[^}]*\}\s*\}'
    bare_matches = re.findall(bare_pattern, text)
    
    for match in bare_matches:
        try:
            import json
            parsed = json.loads(match.strip())
            if 'name' in parsed and not any(tc['name'] == parsed['name'] for tc in tool_calls):
                tool_calls.append({
                    "name": parsed['name'],
                    "arguments": parsed.get('arguments', parsed.get('args', {}))
                })
        except:
            pass
    
    return tool_calls
