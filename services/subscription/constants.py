# ==========================================================
# SUBSCRIPTION FEATURE REGISTRY
# Purpose: This is the central 'Menu' for the entire app.
# 
# DESIGN CHOICE:
# Developers should add new keys here whenever they create 
# a new pro feature. This file acts as the single source of 
# truth for both the Code and the Admin Dashboard.
# ==========================================================

class FeatureKeys:
    # --- Portfolio Tier ---
    PORTFOLIO_SCORE = "portfolio_score"
    ADVANCED_ANALYTICS = "advanced_analytics"
    WEALTH_HISTORY = "wealth_history"
    
    # --- Analysis Tier ---
    AI_INSIGHTS = "ai_insights"
    REAL_TIME_DATA = "real_time_data"
    
    # --- Generic Tiers (For simple setups) ---
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    ELITE = "elite"

    @classmethod
    def get_all(cls):
        """
        Returns a list of all defined feature keys.
        Used by the Admin API to show a 'Checklist' on the dashboard.
        """
        # We filter out internal python attributes and the method itself
        return [
            value for key, value in cls.__dict__.items() 
            if not key.startswith('__') and isinstance(value, str) and key != 'get_all'
        ]
