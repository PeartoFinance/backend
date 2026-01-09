"""
Country Filter Utility for Admin Routes
Provides helper to get country context from request headers
"""
from flask import request


def get_country_context():
    """
    Get country context from request headers
    Returns (is_global, country_code)
    - is_global: True if no specific country (show all)
    - country_code: The country code from header, or None for global
    """
    country_code = request.headers.get('X-Admin-Country', '').strip().upper()
    
    if not country_code or country_code == 'GLOBAL':
        return True, None
    
    return False, country_code


def apply_country_filter(query, model, country_code_field='country_code'):
    """
    Apply country filter to a SQLAlchemy query
    
    Args:
        query: SQLAlchemy query object
        model: The model class to filter
        country_code_field: Name of the country_code column (default: 'country_code')
    
    Returns:
        Filtered query
    """
    is_global, country_code = get_country_context()
    
    if not is_global and country_code:
        # Get the column from the model
        column = getattr(model, country_code_field, None)
        if column is not None:
            return query.filter(column == country_code)
    
    return query


def get_country_for_create():
    """
    Get country code to use when creating new records
    Returns the header value or 'US' as default
    """
    is_global, country_code = get_country_context()
    return country_code if country_code else 'US'
