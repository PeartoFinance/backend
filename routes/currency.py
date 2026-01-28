"""
Currency API Routes
Stateless endpoints for currency conversion and exchange rates.
"""
from flask import Blueprint, request, jsonify
from services.currency_service import convert_usd_to_target, get_all_available_rates

currency_bp = Blueprint('currency', __name__, url_prefix='/api/currency')

@currency_bp.route('/convert', methods=['GET'])
def convert_currency():
    """
    Convert USD amount to target currency.
    Example: /api/currency/convert?amount=100&to=NPR
    """
    amount = request.args.get('amount')
    target = request.args.get('to')
    
    if not amount or not target:
        return jsonify({
            'status': 'error',
            'message': 'Missing required parameters: amount and to'
        }), 400
        
    try:
        amount_val = float(amount)
    except ValueError:
        return jsonify({
            'status': 'error',
            'message': 'Invalid amount format. Must be a number.'
        }), 400
        
    result = convert_usd_to_target(amount_val, target)
    
    if result['status'] == 'error':
        return jsonify(result), 404
        
    return jsonify(result)

@currency_bp.route('/rates', methods=['GET'])
def get_rates():
    """
    Get all available exchange rates.
    """
    rates = get_all_available_rates()
    return jsonify({
        'status': 'success',
        'rates': rates
    })
