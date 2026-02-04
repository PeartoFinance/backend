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
    # --- Free Tier Features ---
    PORTFOLIO_TRACKING = "portfolio_tracking"
    REAL_TIME_DATA = "real_time_data"
    
    # --- Pro Tier Features (Upgrade Required) ---
    ADVANCED_CHARTS = "advanced_charts"
    AI_INSIGHTS = "ai_insights"
    DOWNLOAD_REPORTS = "download_reports"
    UNLIMITED_ALERTS = "unlimited_alerts"
    
    # --- Pro Yearly Tier (All Pro + Extras) ---
    PRIORITY_SUPPORT = "priority_support"
    
    # --- Legacy/Generic Tiers (For backward compatibility) ---
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    ELITE = "elite"
    
    # --- Rate Limits (Numeric features) ---
    MAX_WATCHLISTS = "max_watchlists"
    MAX_PORTFOLIOS = "max_portfolios"
    MAX_ALERTS = "max_alerts"

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


# ==========================================================
# USAGE LIMITS REGISTRY
# Purpose: Define default limits for each plan tier.
# These can be overridden in the plan's 'features' JSON.
# ==========================================================

class UsageLimits:
    """
    Default usage limits. Admins can override these per-plan via the dashboard.
    Format: feature_key -> { limit: number, period: 'daily'|'monthly'|'total' }
    """
    
    # Limit keys (stored in plan.features JSON)
    AI_QUERIES_LIMIT = "ai_queries_limit"
    ADVANCED_CHARTS_LIMIT = "advanced_charts_limit"
    DOWNLOAD_REPORTS_LIMIT = "download_reports_limit"
    ALERTS_LIMIT = "alerts_limit"
    CHART_TEMPLATES_LIMIT = "chart_templates_limit"
    COMPARISON_LIMIT = "comparison_limit"
    SAVED_SCREENERS_LIMIT = "saved_screeners_limit"
    
    # Default limits by tier
    FREE_DEFAULTS = {
        "ai_queries_limit": 5,           # per day
        "advanced_charts_limit": 3,      # per day
        "download_reports_limit": 3,     # per month
        "alerts_limit": 3,               # total
        "chart_templates_limit": 1,      # total
        "comparison_limit": 5,           # per day
        "saved_screeners_limit": 1,      # total
    }
    
    PRO_DEFAULTS = {
        "ai_queries_limit": -1,          # -1 = unlimited
        "advanced_charts_limit": -1,
        "download_reports_limit": -1,
        "alerts_limit": -1,
        "chart_templates_limit": -1,
        "comparison_limit": -1,
        "saved_screeners_limit": -1,
    }
    
    # Period definitions for each limit
    PERIODS = {
        "ai_queries_limit": "daily",
        "advanced_charts_limit": "daily",
        "download_reports_limit": "monthly",
        "alerts_limit": "total",
        "chart_templates_limit": "total",
        "comparison_limit": "daily",
        "saved_screeners_limit": "total",
    }
    
    @classmethod
    def get_limit_keys(cls):
        """Returns list of all limit keys for Admin UI."""
        return [
            {"key": cls.AI_QUERIES_LIMIT, "display": "AI Queries", "period": "daily"},
            {"key": cls.ADVANCED_CHARTS_LIMIT, "display": "Advanced Charts", "period": "daily"},
            {"key": cls.DOWNLOAD_REPORTS_LIMIT, "display": "Download Reports", "period": "monthly"},
            {"key": cls.ALERTS_LIMIT, "display": "Price Alerts", "period": "total"},
            {"key": cls.CHART_TEMPLATES_LIMIT, "display": "Chart Templates", "period": "total"},
            # New Limits
            {"key": cls.COMPARISON_LIMIT, "display": "Stock Comparisons", "period": "daily"},
            {"key": cls.SAVED_SCREENERS_LIMIT, "display": "Saved Screeners", "period": "total"},
        ]


