"""
Chart API Routes
Drawings, templates, indicators, and AI analysis endpoints
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
import uuid
from routes.decorators import auth_required
from models import db
from models.chart import ChartDrawing, ChartTemplate, ChartIndicatorSettings, DetectedPattern

chart_bp = Blueprint('chart', __name__)


# ============== DRAWINGS ==============

@chart_bp.route('/drawings/<symbol>', methods=['GET'])
@auth_required
def get_drawings(symbol):
    """Get all drawings for a symbol"""
    drawings = ChartDrawing.query.filter_by(
        user_id=request.user.id,
        symbol=symbol.upper()
    ).order_by(ChartDrawing.created_at).all()
    
    return jsonify([d.to_dict() for d in drawings])


@chart_bp.route('/drawings/<symbol>', methods=['POST'])
@auth_required
def save_drawing(symbol):
    """Save a new drawing"""
    data = request.get_json()
    
    drawing = ChartDrawing(
        id=str(uuid.uuid4()),
        user_id=request.user.id,
        symbol=symbol.upper(),
        drawing_type=data.get('drawingType', 'trendline'),
        data=data.get('data', {}),
        is_visible=data.get('isVisible', True)
    )
    
    db.session.add(drawing)
    db.session.commit()
    
    return jsonify(drawing.to_dict()), 201


@chart_bp.route('/drawings/<symbol>/<drawing_id>', methods=['PUT'])
@auth_required
def update_drawing(symbol, drawing_id):
    """Update a drawing"""
    drawing = ChartDrawing.query.filter_by(
        id=drawing_id,
        user_id=request.user.id,
        symbol=symbol.upper()
    ).first()
    
    if not drawing:
        return jsonify({'error': 'Drawing not found'}), 404
    
    data = request.get_json()
    
    if 'data' in data:
        drawing.data = data['data']
    if 'isVisible' in data:
        drawing.is_visible = data['isVisible']
    if 'drawingType' in data:
        drawing.drawing_type = data['drawingType']
    
    db.session.commit()
    
    return jsonify(drawing.to_dict())


@chart_bp.route('/drawings/<symbol>/<drawing_id>', methods=['DELETE'])
@auth_required
def delete_drawing(symbol, drawing_id):
    """Delete a drawing"""
    drawing = ChartDrawing.query.filter_by(
        id=drawing_id,
        user_id=request.user.id,
        symbol=symbol.upper()
    ).first()
    
    if not drawing:
        return jsonify({'error': 'Drawing not found'}), 404
    
    db.session.delete(drawing)
    db.session.commit()
    
    return jsonify({'message': 'Drawing deleted'})


@chart_bp.route('/drawings/<symbol>/bulk', methods=['POST'])
@auth_required
def bulk_save_drawings(symbol):
    """Bulk save/sync all drawings for a symbol"""
    data = request.get_json()
    drawings_data = data.get('drawings', [])
    
    # Delete existing drawings
    ChartDrawing.query.filter_by(
        user_id=request.user.id,
        symbol=symbol.upper()
    ).delete()
    
    # Create new drawings
    for d in drawings_data:
        drawing = ChartDrawing(
            id=d.get('id', str(uuid.uuid4())),
            user_id=request.user.id,
            symbol=symbol.upper(),
            drawing_type=d.get('drawingType', 'trendline'),
            data=d.get('data', {}),
            is_visible=d.get('isVisible', True)
        )
        db.session.add(drawing)
    
    db.session.commit()
    
    return jsonify({'message': f'Saved {len(drawings_data)} drawings'})


# ============== TEMPLATES ==============

@chart_bp.route('/templates', methods=['GET'])
@auth_required
def get_templates():
    """Get all user templates"""
    templates = ChartTemplate.query.filter_by(
        user_id=request.user.id
    ).order_by(ChartTemplate.created_at.desc()).all()
    
    return jsonify([t.to_dict() for t in templates])


@chart_bp.route('/templates', methods=['POST'])
@auth_required
def create_template():
    """Create a new chart template"""
    data = request.get_json()
    
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'error': 'Template name required'}), 400
    
    # If setting as default, unset other defaults
    if data.get('isDefault'):
        ChartTemplate.query.filter_by(
            user_id=request.user.id,
            is_default=True
        ).update({'is_default': False})
    
    template = ChartTemplate(
        id=str(uuid.uuid4()),
        user_id=request.user.id,
        name=name,
        description=data.get('description'),
        is_default=data.get('isDefault', False),
        config=data.get('config', {})
    )
    
    db.session.add(template)
    db.session.commit()
    
    return jsonify(template.to_dict()), 201


@chart_bp.route('/templates/<template_id>', methods=['DELETE'])
@auth_required
def delete_template(template_id):
    """Delete a template"""
    template = ChartTemplate.query.filter_by(
        id=template_id,
        user_id=request.user.id
    ).first()
    
    if not template:
        return jsonify({'error': 'Template not found'}), 404
    
    db.session.delete(template)
    db.session.commit()
    
    return jsonify({'message': 'Template deleted'})


# ============== INDICATORS ==============

@chart_bp.route('/indicators', methods=['GET'])
def get_available_indicators():
    """Get list of available technical indicators"""
    indicators = [
        {
            'id': 'sma',
            'name': 'Simple Moving Average',
            'category': 'trend',
            'defaultParams': {'period': 20},
            'description': 'Arithmetic mean of prices over a period'
        },
        {
            'id': 'ema',
            'name': 'Exponential Moving Average',
            'category': 'trend',
            'defaultParams': {'period': 20},
            'description': 'Weighted moving average giving more weight to recent prices'
        },
        {
            'id': 'rsi',
            'name': 'Relative Strength Index',
            'category': 'momentum',
            'defaultParams': {'period': 14},
            'description': 'Momentum oscillator measuring speed and change of price movements'
        },
        {
            'id': 'macd',
            'name': 'MACD',
            'category': 'momentum',
            'defaultParams': {'fastPeriod': 12, 'slowPeriod': 26, 'signalPeriod': 9},
            'description': 'Moving Average Convergence Divergence trend-following indicator'
        },
        {
            'id': 'bollinger',
            'name': 'Bollinger Bands',
            'category': 'volatility',
            'defaultParams': {'period': 20, 'stdDev': 2},
            'description': 'Volatility bands placed above and below a moving average'
        },
        {
            'id': 'stochastic',
            'name': 'Stochastic Oscillator',
            'category': 'momentum',
            'defaultParams': {'kPeriod': 14, 'dPeriod': 3},
            'description': 'Momentum indicator comparing closing price to price range'
        },
        {
            'id': 'atr',
            'name': 'Average True Range',
            'category': 'volatility',
            'defaultParams': {'period': 14},
            'description': 'Volatility indicator showing degree of price movement'
        },
        {
            'id': 'vwap',
            'name': 'Volume Weighted Average Price',
            'category': 'volume',
            'defaultParams': {},
            'description': 'Average price weighted by volume, used as trading benchmark'
        },
        {
            'id': 'obv',
            'name': 'On-Balance Volume',
            'category': 'volume',
            'defaultParams': {},
            'description': 'Cumulative volume indicator to show buying/selling pressure'
        },
        {
            'id': 'ichimoku',
            'name': 'Ichimoku Cloud',
            'category': 'trend',
            'defaultParams': {'conversionPeriod': 9, 'basePeriod': 26, 'spanPeriod': 52},
            'description': 'All-in-one indicator showing support/resistance, trend, and momentum'
        }
    ]
    
    return jsonify(indicators)


@chart_bp.route('/indicators/settings', methods=['GET'])
@auth_required
def get_indicator_settings():
    """Get user's saved indicator settings"""
    symbol = request.args.get('symbol')
    
    query = ChartIndicatorSettings.query.filter_by(user_id=request.user.id)
    if symbol:
        query = query.filter((ChartIndicatorSettings.symbol == symbol.upper()) | (ChartIndicatorSettings.symbol == None))
    
    settings = query.all()
    return jsonify([s.to_dict() for s in settings])


@chart_bp.route('/indicators/settings', methods=['POST'])
@auth_required
def save_indicator_settings():
    """Save indicator settings"""
    data = request.get_json()
    
    setting = ChartIndicatorSettings(
        user_id=request.user.id,
        symbol=data.get('symbol', '').upper() if data.get('symbol') else None,
        indicator_type=data.get('indicatorType'),
        params=data.get('params', {}),
        is_active=data.get('isActive', True),
        color=data.get('color')
    )
    
    db.session.add(setting)
    db.session.commit()
    
    return jsonify(setting.to_dict()), 201


# ============== AI ANALYSIS ==============

@chart_bp.route('/analyze/<symbol>', methods=['POST'])
@auth_required
async def analyze_chart(symbol):
    """AI-powered chart analysis"""
    from services.ai_service import ai_service
    
    data = request.get_json() or {}
    chart_data = data.get('chartData', {})
    timeframe = data.get('timeframe', '1D')
    
    # Build analysis prompt
    prompt = f"""Analyze the {symbol.upper()} chart on {timeframe} timeframe.

Chart Data Summary:
- Current Price: ${chart_data.get('currentPrice', 'N/A')}
- Period Change: {chart_data.get('changePercent', 'N/A')}%
- High: ${chart_data.get('high', 'N/A')}
- Low: ${chart_data.get('low', 'N/A')}
- Volume: {chart_data.get('volume', 'N/A')}

Provide:
1. **Technical Analysis** - Key support/resistance levels
2. **Entry/Exit Signals** - Potential entry and exit points
3. **Stop-Loss Zones** - Recommended stop-loss placement
4. **Pattern Detection** - Any chart patterns visible
5. **Risk Assessment** - Overall risk level (low/medium/high)"""

    try:
        result = await ai_service.chat(
            message=prompt,
            context={
                'pageType': 'chart',
                'pageData': {
                    'symbol': symbol.upper(),
                    'timeframe': timeframe,
                    **chart_data
                }
            },
            options={'max_tokens': 800}
        )
        
        return jsonify({
            'success': result.get('success', False),
            'analysis': result.get('response', ''),
            'symbol': symbol.upper(),
            'timeframe': timeframe,
            'provider': result.get('provider', 'AI')
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'analysis': 'Unable to generate analysis at this time.'
        }), 500


# ============== PATTERNS ==============

@chart_bp.route('/patterns/<symbol>', methods=['GET'])
def get_patterns(symbol):
    """Get detected patterns for a symbol"""
    timeframe = request.args.get('timeframe', '1D')
    
    patterns = DetectedPattern.query.filter_by(
        symbol=symbol.upper(),
        timeframe=timeframe
    ).filter(
        DetectedPattern.expires_at > datetime.utcnow()
    ).order_by(DetectedPattern.confidence.desc()).limit(10).all()
    
    return jsonify([p.to_dict() for p in patterns])
