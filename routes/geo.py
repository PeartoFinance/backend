"""
Geo-detection API Routes
- Country detection and list of supported countries
"""
from flask import Blueprint, request, jsonify
import requests
from models.db import Country

geo_bp = Blueprint('geo', __name__)


@geo_bp.route('/geo', methods=['GET'])
def detect_country():
    """Detect user's country from IP address"""
    # Get client IP - check various headers for proxied requests
    client_ip = (
        request.headers.get('X-Forwarded-For', '').split(',')[0].strip() or
        request.headers.get('X-Real-IP') or
        request.remote_addr
    )
    
    # Default to US
    country_code = 'US'
    
    # Try to detect from IP using a free geo service
    try:
        # Skip localhost/private IPs
        if client_ip not in ('127.0.0.1', 'localhost', '::1'):
            response = requests.get(
                f'http://ip-api.com/json/{client_ip}?fields=countryCode',
                timeout=2
            )
            if response.ok:
                data = response.json()
                country_code = data.get('countryCode', 'US')
    except Exception:
        pass  # Use default
    
    # Check if country is in our supported list
    country = Country.query.get(country_code)
    if not country or not country.is_active:
        country_code = 'US'
    
    return jsonify({
        'country': country_code,
        'ip': client_ip,
        'source': 'auto'
    })


@geo_bp.route('/countries', methods=['GET'])
def get_countries():
    """Get list of supported countries"""
    active_only = request.args.get('active', 'true').lower() != 'false'
    
    query = Country.query
    if active_only:
        query = query.filter(Country.is_active == True)
    
    countries = query.order_by(Country.sort_order, Country.name).all()
    
    return jsonify({
        'countries': [c.to_dict() for c in countries]
    })


@geo_bp.route('/country/<code>', methods=['GET'])
def get_country(code):
    """Get single country by code"""
    country = Country.query.get(code.upper())
    
    if not country:
        return jsonify({'error': 'Country not found'}), 404
    
    return jsonify(country.to_dict())
