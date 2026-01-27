"""
Portfolio Service
Handles complex logic for portfolio analysis and health scoring.
"""
from models import db, UserPortfolio, PortfolioHolding, UserInvestmentGoal, MarketData
from decimal import Decimal

def calculate_portfolio_health(user_id):
    """
    Calculates a health score (0-100) for a user's portfolio 
    by comparing actual holdings against their set goals.
    """
    
    # 1. Fetch User Goals
    # This tells us what the user WANTS (e.g., 60% stocks, 10% crypto)
    goals = UserInvestmentGoal.query.filter_by(user_id=user_id).first()
    
    # 2. Fetch User Holdings
    # This tells us what the user actually HAS right now
    holdings = PortfolioHolding.query.join(UserPortfolio).filter(UserPortfolio.user_id == user_id).all()
    
    # If no goals are set, we can't calculate a score relative to a target
    if not goals:
        return {
            "score": 0,
            "status": "No Goals Set",
            "message": "Please set your investment goals first to calculate your health score.",
            "needs_setup": True
        }
        
    # If no holdings, the score is 0
    if not holdings:
        return {
            "score": 0,
            "status": "Empty Portfolio",
            "message": "Add some assets to your portfolio to see your health score.",
            "needs_holdings": True
        }

    # 3. Calculate Total Portfolio Value
    total_value = sum(Decimal(str(h.current_value or 0)) for h in holdings)
    
    if total_value == 0:
        return {"score": 0, "message": "Portfolio has no current value."}

    # 4. Calculate Actual Allocation by Asset Type
    # We group holdings into categories like 'stock', 'crypto', etc.
    actual_alloc = {
        'stocks': Decimal('0'),
        'crypto': Decimal('0'),
        'bonds': Decimal('0'),
        'cash': Decimal('0'),
        'commodities': Decimal('0')
    }
    
    for h in holdings:
        asset_type = (h.asset_type or 'stock').lower()
        val = Decimal(str(h.current_value or 0))
        
        if 'stock' in asset_type:
            actual_alloc['stocks'] += val
        elif 'crypto' in asset_type:
            actual_alloc['crypto'] += val
        elif 'bond' in asset_type:
            actual_alloc['bonds'] += val
        elif 'cash' in asset_type:
            actual_alloc['cash'] += val
        else:
            actual_alloc['commodities'] += val

    # Convert actual values to percentages
    actual_percents = {k: (v / total_value) * 100 for k, v in actual_alloc.items()}

    # 5. Define Target Percentages from User Goals
    target_percents = {
        'stocks': Decimal(str(goals.target_stocks_percent or 0)),
        'crypto': Decimal(str(goals.target_crypto_percent or 0)),
        'bonds': Decimal(str(goals.target_bonds_percent or 0)),
        'cash': Decimal(str(goals.target_cash_percent or 0)),
        'commodities': Decimal(str(goals.target_commodities_percent or 0))
    }

    # 6. Calculate the Score (Allocation Gap)
    # We subtract points for every percentage point they are away from their target
    total_deviation = 0
    recommendations = []
    
    for asset, target in target_percents.items():
        actual = actual_percents[asset]
        diff = actual - target # How far off are we?
        
        total_deviation += abs(diff)
        
        # If the gap is more than 10%, add a recommendation
        if diff > 10:
            recommendations.append(f"Your {asset} allocation is {diff:.1f}% higher than your target. Consider selling some to rebalance.")
        elif diff < -10:
            recommendations.append(f"Your {asset} allocation is {abs(diff):.1f}% lower than your target. Consider adding more.")

    # Base score is 100. We subtract the average deviation.
    # A perfectly balanced portfolio (0 deviation) gets 100.
    score = max(0, 100 - (total_deviation / 2)) # Divide by 2 because deviation is counted twice (over in one, under in another)

    # 7. Benchmark Comparison
    # Compare user's total gain % vs the benchmark's gain %
    benchmark_info = None
    if goals.benchmark_symbol:
        benchmark = MarketData.query.filter_by(symbol=goals.benchmark_symbol).first()
        if benchmark:
            benchmark_info = {
                "symbol": benchmark.symbol,
                "name": benchmark.name or benchmark.symbol,
                "price": float(benchmark.price) if benchmark.price else 0,
                "change_percent": float(benchmark.change_percent) if benchmark.change_percent else 0
            }

    # 8. Determine Status Label
    status = "Excellent"
    if score < 50: status = "Needs Attention"
    elif score < 75: status = "Good"
    elif score < 90: status = "Very Good"

    return {
        "score": round(float(score), 1),
        "status": status,
        "total_value": float(total_value),
        "actual_allocation": {k: float(v) for k, v in actual_percents.items()},
        "target_allocation": {k: float(v) for k, v in target_percents.items()},
        "recommendations": recommendations[:3],
        "benchmark": benchmark_info
    }
