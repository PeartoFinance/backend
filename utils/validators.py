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

def safe_pagination(limit_param, offset_param, max_limit=100, max_offset=10000):
    """
    Safely validate pagination parameters to prevent DoS attacks.
    
    Args:
        limit_param: Raw limit from request (e.g., request.args.get('limit'))
        offset_param: Raw offset from request (e.g., request.args.get('offset'))
        max_limit: Maximum allowed limit (default 100)
        max_offset: Maximum allowed offset (default 10000 records)
    
    Returns:
        Tuple of (limit, offset) safe values
    
    Example:
        limit, offset = safe_pagination(
            request.args.get('limit'),
            request.args.get('offset'),
            max_limit=50,
            max_offset=5000
        )
    """
    # Convert to integers safely, default to 0 if invalid
    limit = safe_int(limit_param, 10)
    offset = safe_int(offset_param, 0)
    
    # Enforce upper bounds (prevents full table scans)
    limit = min(max(limit, 1), max_limit)  # Between 1 and max_limit
    offset = max(0, min(offset, max_offset))  # Between 0 and max_offset
    
    return limit, offset