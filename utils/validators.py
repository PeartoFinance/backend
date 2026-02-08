"""
Input Validation Utilities
Safe conversion functions to prevent 500 errors from malformed URL parameters.
"""

def safe_int(value, default=0):
    """
    Safely convert a value to an integer.
    Returns the default value if conversion fails.
    """
    try:
        if value is None:
            return default
        return int(value)
    except (ValueError, TypeError):
        return default

def safe_float(value, default=0.0):
    """
    Safely convert a value to a float.
    Returns the default value if conversion fails.
    """
    try:
        if value is None:
            return default
        return float(value)
    except (ValueError, TypeError):
        return default
