"""
AI Tools - Tool definitions and executors for AI chat
"""
import re
import math
from typing import Dict, Any, List, Optional
from models.base import db


# Tool definitions for OpenAI function calling format
AI_TOOLS = [
    {
        "name": "get_stock_quote",
        "description": "Get real-time stock price and information for a given symbol",
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
        "name": "get_forex_rates",
        "description": "Get forex exchange rates",
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
        "description": "Search for financial news",
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
    """Get stock quote from database"""
    from models import MarketData
    
    stock = MarketData.query.filter(
        MarketData.symbol == symbol.upper(),
        MarketData.asset_type == 'stock'
    ).first()
    
    if not stock:
        return {"error": f"Stock {symbol} not found"}
    
    return {
        "symbol": stock.symbol,
        "name": stock.name,
        "price": float(stock.price) if stock.price else 0,
        "change": float(stock.change) if stock.change else 0,
        "changePercent": float(stock.change_percent) if stock.change_percent else 0,
        "volume": stock.volume,
        "marketCap": stock.market_cap,
        "source": "database"
    }


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
    
    return tool_calls
