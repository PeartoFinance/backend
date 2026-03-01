"""
Chart Analysis API Routes
AI-powered chart image analysis (via Groq Vision) + Trade Journal CRUD
"""
import uuid
import asyncio
import base64
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from routes.decorators import auth_required
from models import db, TradeJournal, TradeReview
from sqlalchemy import func

chart_analysis_bp = Blueprint('chart_analysis', __name__)

# Max image size: 4MB (Groq base64 limit)
MAX_IMAGE_SIZE = 4 * 1024 * 1024
ALLOWED_IMAGE_TYPES = {'image/jpeg', 'image/png', 'image/webp'}


def _run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        try:
            loop.run_until_complete(loop.shutdown_asyncgens())
        except Exception:
            pass
        loop.close()


CHART_ANALYSIS_SYSTEM_PROMPT = """You are an expert financial chart analyst specializing in technical analysis for stocks, crypto, and forex markets.

When analyzing a chart image, provide a structured analysis with these sections:

## 📊 Chart Overview
- Identify the asset, timeframe, and chart type visible
- Current trend direction (bullish/bearish/sideways)

## 🔑 Key Levels
- **Support levels**: Identify 2-3 key support zones
- **Resistance levels**: Identify 2-3 key resistance zones

## 📐 Pattern Detection
- Identify any chart patterns (head & shoulders, triangles, flags, wedges, double top/bottom, etc.)
- Note candlestick patterns if visible

## 📈 Technical Indicators
- Analyze any visible indicators (moving averages, RSI, MACD, Bollinger Bands, etc.)
- Note divergences if present

## 🎯 Trade Setup
- **Entry zone**: Suggested entry area
- **Stop-loss**: Recommended stop-loss placement with reasoning
- **Take-profit targets**: 1-3 target levels
- **Risk/Reward ratio**: Calculate approximate R:R

## ⚠️ Risk Assessment
- Overall risk level: Low / Medium / High
- Key risks and invalidation levels

Keep the analysis concise, actionable, and professional. Use numbers and price levels where visible.
Disclaimer: This is AI-generated analysis for educational purposes only, not financial advice."""


# ============== CHART IMAGE ANALYSIS ==============

@chart_analysis_bp.route('/analyze', methods=['POST'])
@auth_required
def analyze_chart_image():
    """Analyze an uploaded chart image using Groq Vision AI"""
    from services.ai_provider import vision_completion

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body required'}), 400

    image_base64 = data.get('image')
    if not image_base64:
        return jsonify({'error': 'Image data required'}), 400

    # Validate image size
    try:
        image_bytes = base64.b64decode(image_base64)
        if len(image_bytes) > MAX_IMAGE_SIZE:
            return jsonify({'error': 'Image too large. Maximum 4MB allowed.'}), 400
    except Exception:
        return jsonify({'error': 'Invalid base64 image data'}), 400

    image_type = data.get('imageType', 'image/jpeg')
    if image_type not in ALLOWED_IMAGE_TYPES:
        return jsonify({'error': f'Unsupported image type. Allowed: {", ".join(ALLOWED_IMAGE_TYPES)}'}), 400

    symbol = data.get('symbol', 'Unknown')
    timeframe = data.get('timeframe', '1D')
    market_type = data.get('marketType', 'stock')
    analysis_mode = data.get('mode', 'general')  # general, swing, scalp

    # Build prompt based on mode
    mode_context = ''
    if analysis_mode == 'swing':
        mode_context = '\nFocus on SWING TRADE setups (multi-day to multi-week holds). Look for major trend structures, key S/R levels, and swing entry points.'
    elif analysis_mode == 'scalp':
        mode_context = '\nFocus on SCALP TRADE setups (minutes to hours). Look for quick entry/exit points, momentum signals, and micro price action.'

    prompt = f"""Analyze this {market_type} chart for {symbol} on the {timeframe} timeframe.{mode_context}

Provide a detailed technical analysis following the structured format."""

    try:
        result = _run_async(vision_completion(
            text_prompt=prompt,
            image_base64=image_base64,
            image_type=image_type,
            max_tokens=1500,
        ))

        return jsonify({
            'success': result.get('success', False),
            'analysis': result.get('content', ''),
            'symbol': symbol,
            'timeframe': timeframe,
            'marketType': market_type,
            'mode': analysis_mode,
            'provider': result.get('provider', 'groq'),
            'model': result.get('model', ''),
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@chart_analysis_bp.route('/analyze/swing', methods=['POST'])
@auth_required
def analyze_swing():
    """Swing trade analysis shortcut — sets mode to swing"""
    data = request.get_json() or {}
    data['mode'] = 'swing'
    # Re-inject modified data
    import flask
    with flask.current_app.test_request_context(
        '/analyze', method='POST', json=data,
        headers=dict(request.headers)
    ):
        flask.request = request
    # Just call the main analyze with mode set
    from services.ai_provider import vision_completion

    image_base64 = data.get('image')
    if not image_base64:
        return jsonify({'error': 'Image data required'}), 400

    try:
        image_bytes = base64.b64decode(image_base64)
        if len(image_bytes) > MAX_IMAGE_SIZE:
            return jsonify({'error': 'Image too large. Maximum 4MB allowed.'}), 400
    except Exception:
        return jsonify({'error': 'Invalid base64 image data'}), 400

    image_type = data.get('imageType', 'image/jpeg')
    symbol = data.get('symbol', 'Unknown')
    timeframe = data.get('timeframe', '1D')
    market_type = data.get('marketType', 'stock')

    prompt = f"""Analyze this {market_type} chart for {symbol} on the {timeframe} timeframe.
Focus on SWING TRADE setups (multi-day to multi-week holds).
Identify major trend structure, key support/resistance levels, optimal swing entry points,
and multi-target exit strategy. Include position sizing suggestions based on the chart structure."""

    try:
        result = _run_async(vision_completion(
            text_prompt=prompt,
            image_base64=image_base64,
            image_type=image_type,
            max_tokens=1500,
        ))
        return jsonify({
            'success': result.get('success', False),
            'analysis': result.get('content', ''),
            'symbol': symbol, 'timeframe': timeframe,
            'marketType': market_type, 'mode': 'swing',
            'provider': result.get('provider', 'groq'),
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@chart_analysis_bp.route('/analyze/scalp', methods=['POST'])
@auth_required
def analyze_scalp():
    """Scalp trade analysis shortcut"""
    from services.ai_provider import vision_completion

    data = request.get_json() or {}
    image_base64 = data.get('image')
    if not image_base64:
        return jsonify({'error': 'Image data required'}), 400

    try:
        image_bytes = base64.b64decode(image_base64)
        if len(image_bytes) > MAX_IMAGE_SIZE:
            return jsonify({'error': 'Image too large. Maximum 4MB allowed.'}), 400
    except Exception:
        return jsonify({'error': 'Invalid base64 image data'}), 400

    image_type = data.get('imageType', 'image/jpeg')
    symbol = data.get('symbol', 'Unknown')
    timeframe = data.get('timeframe', '5m')
    market_type = data.get('marketType', 'stock')

    prompt = f"""Analyze this {market_type} chart for {symbol} on the {timeframe} timeframe.
Focus on SCALP TRADE setups (minutes to hours). Identify quick entry/exit points,
momentum signals, order flow context, and micro price action patterns.
Include tight stop-loss placement and quick-profit target levels."""

    try:
        result = _run_async(vision_completion(
            text_prompt=prompt,
            image_base64=image_base64,
            image_type=image_type,
            max_tokens=1200,
        ))
        return jsonify({
            'success': result.get('success', False),
            'analysis': result.get('content', ''),
            'symbol': symbol, 'timeframe': timeframe,
            'marketType': market_type, 'mode': 'scalp',
            'provider': result.get('provider', 'groq'),
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@chart_analysis_bp.route('/pre-trade', methods=['POST'])
@auth_required
def pre_trade_calculator():
    """AI-enhanced pre-trade risk/reward calculation"""
    from services.ai_provider import chat_completion

    data = request.get_json() or {}
    entry = data.get('entryPrice')
    stop_loss = data.get('stopLoss')
    take_profit = data.get('takeProfit')
    position_size = data.get('positionSize')
    account_balance = data.get('accountBalance')
    symbol = data.get('symbol', 'Unknown')
    direction = data.get('direction', 'long')

    if not all([entry, stop_loss, take_profit]):
        return jsonify({'error': 'entryPrice, stopLoss, and takeProfit are required'}), 400

    entry = float(entry)
    stop_loss = float(stop_loss)
    take_profit = float(take_profit)
    position_size = float(position_size) if position_size else None
    account_balance = float(account_balance) if account_balance else None

    # Calculate risk/reward
    if direction == 'long':
        risk_per_unit = entry - stop_loss
        reward_per_unit = take_profit - entry
    else:
        risk_per_unit = stop_loss - entry
        reward_per_unit = entry - take_profit

    rr_ratio = abs(reward_per_unit / risk_per_unit) if risk_per_unit != 0 else 0

    risk_amount = abs(risk_per_unit * position_size) if position_size else None
    reward_amount = abs(reward_per_unit * position_size) if position_size else None
    risk_percent = (risk_amount / account_balance * 100) if risk_amount and account_balance else None

    calc = {
        'symbol': symbol,
        'direction': direction,
        'entryPrice': entry,
        'stopLoss': stop_loss,
        'takeProfit': take_profit,
        'riskPerUnit': round(abs(risk_per_unit), 6),
        'rewardPerUnit': round(abs(reward_per_unit), 6),
        'rrRatio': round(rr_ratio, 2),
        'positionSize': position_size,
        'riskAmount': round(risk_amount, 2) if risk_amount else None,
        'rewardAmount': round(reward_amount, 2) if reward_amount else None,
        'riskPercent': round(risk_percent, 2) if risk_percent else None,
    }

    # Suggested position size based on 1-2% risk rule
    if account_balance and risk_per_unit != 0:
        calc['suggestedSize1Pct'] = round(abs(account_balance * 0.01 / risk_per_unit), 4)
        calc['suggestedSize2Pct'] = round(abs(account_balance * 0.02 / risk_per_unit), 4)

    # Get AI opinion
    prompt = f"""Evaluate this trade setup for {symbol} ({direction}):
- Entry: ${entry}, Stop-Loss: ${stop_loss}, Take-Profit: ${take_profit}
- Risk/Reward Ratio: {rr_ratio:.2f}
- Risk Amount: ${risk_amount:.2f if risk_amount else 'N/A'}
- Account Risk: {risk_percent:.1f}% of balance

Give a brief (3-4 sentence) assessment: Is this a good R:R? Is the stop too tight/loose?
Any position sizing advice? Rate the setup: ⭐ Poor / ⭐⭐ Fair / ⭐⭐⭐ Good / ⭐⭐⭐⭐ Very Good / ⭐⭐⭐⭐⭐ Excellent"""

    try:
        ai_result = _run_async(chat_completion(
            messages=[
                {"role": "system", "content": "You are a professional trading risk analyst. Be concise and practical."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
        ))
        calc['aiAssessment'] = ai_result.get('content', '')
        calc['success'] = True
    except Exception:
        calc['aiAssessment'] = ''
        calc['success'] = True

    return jsonify(calc)


# ============== TRADE JOURNAL ==============

@chart_analysis_bp.route('/journal', methods=['GET'])
@auth_required
def get_journal_entries():
    """List trade journal entries for the authenticated user"""
    user_id = request.user.id
    status = request.args.get('status')
    market_type = request.args.get('marketType')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = TradeJournal.query.filter_by(user_id=user_id)
    if status:
        query = query.filter_by(status=status)
    if market_type:
        query = query.filter_by(market_type=market_type)

    entries = query.order_by(TradeJournal.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'entries': [e.to_dict() for e in entries.items],
        'total': entries.total,
        'pages': entries.pages,
        'currentPage': page,
    })


@chart_analysis_bp.route('/journal', methods=['POST'])
@auth_required
def create_journal_entry():
    """Create a new trade journal entry"""
    data = request.get_json()
    if not data or not data.get('symbol'):
        return jsonify({'error': 'Symbol is required'}), 400

    entry = TradeJournal(
        id=str(uuid.uuid4()),
        user_id=request.user.id,
        symbol=data['symbol'].upper(),
        market_type=data.get('marketType', 'stock'),
        direction=data.get('direction', 'long'),
        entry_price=data.get('entryPrice'),
        exit_price=data.get('exitPrice'),
        stop_loss=data.get('stopLoss'),
        take_profit=data.get('takeProfit'),
        quantity=data.get('quantity'),
        timeframe=data.get('timeframe'),
        strategy=data.get('strategy'),
        notes=data.get('notes'),
        chart_image_url=data.get('chartImageUrl'),
        analysis_result=data.get('analysisResult'),
        status=data.get('status', 'planned'),
        tags=data.get('tags'),
    )

    db.session.add(entry)
    db.session.commit()
    return jsonify(entry.to_dict()), 201


@chart_analysis_bp.route('/journal/<entry_id>', methods=['GET'])
@auth_required
def get_journal_entry(entry_id):
    """Get a single journal entry with its reviews"""
    entry = TradeJournal.query.filter_by(id=entry_id, user_id=request.user.id).first()
    if not entry:
        return jsonify({'error': 'Entry not found'}), 404

    data = entry.to_dict()
    data['reviews'] = [r.to_dict() for r in entry.reviews.order_by(TradeReview.created_at.desc()).all()]
    return jsonify(data)


@chart_analysis_bp.route('/journal/<entry_id>', methods=['PUT'])
@auth_required
def update_journal_entry(entry_id):
    """Update a trade journal entry"""
    entry = TradeJournal.query.filter_by(id=entry_id, user_id=request.user.id).first()
    if not entry:
        return jsonify({'error': 'Entry not found'}), 404

    data = request.get_json() or {}
    for field in ['symbol', 'market_type', 'direction', 'entry_price', 'exit_price',
                  'stop_loss', 'take_profit', 'quantity', 'timeframe', 'strategy',
                  'notes', 'chart_image_url', 'analysis_result', 'tags']:
        camel = ''.join(w.capitalize() if i else w for i, w in enumerate(field.split('_')))
        if camel in data:
            setattr(entry, field, data[camel])

    if 'status' in data:
        old_status = entry.status
        entry.status = data['status']
        # Auto-set closed_at and calculate PnL when closing
        if data['status'] == 'closed' and old_status != 'closed':
            entry.closed_at = datetime.now(timezone.utc)
            if entry.entry_price and entry.exit_price:
                ep = float(entry.entry_price)
                xp = float(entry.exit_price)
                if entry.direction == 'long':
                    entry.pnl = xp - ep
                    entry.pnl_percent = ((xp - ep) / ep) * 100 if ep else 0
                else:
                    entry.pnl = ep - xp
                    entry.pnl_percent = ((ep - xp) / ep) * 100 if ep else 0
                if entry.quantity:
                    entry.pnl = float(entry.pnl) * float(entry.quantity)

    db.session.commit()
    return jsonify(entry.to_dict())


@chart_analysis_bp.route('/journal/<entry_id>', methods=['DELETE'])
@auth_required
def delete_journal_entry(entry_id):
    """Delete a trade journal entry"""
    entry = TradeJournal.query.filter_by(id=entry_id, user_id=request.user.id).first()
    if not entry:
        return jsonify({'error': 'Entry not found'}), 404

    db.session.delete(entry)
    db.session.commit()
    return jsonify({'success': True})


@chart_analysis_bp.route('/journal/<entry_id>/review', methods=['POST'])
@auth_required
def create_trade_review(entry_id):
    """Generate an AI trade review for a journal entry"""
    from services.ai_provider import chat_completion

    entry = TradeJournal.query.filter_by(id=entry_id, user_id=request.user.id).first()
    if not entry:
        return jsonify({'error': 'Entry not found'}), 404

    data = request.get_json() or {}
    review_type = data.get('reviewType', 'pre-trade')

    # Build context
    trade_info = f"""Symbol: {entry.symbol} ({entry.market_type})
Direction: {entry.direction}
Entry Price: {entry.entry_price or 'Not set'}
Stop-Loss: {entry.stop_loss or 'Not set'}
Take-Profit: {entry.take_profit or 'Not set'}
Timeframe: {entry.timeframe or 'N/A'}
Strategy: {entry.strategy or 'N/A'}
Notes: {entry.notes or 'None'}"""

    if review_type == 'post-trade' and entry.exit_price:
        trade_info += f"""
Exit Price: {entry.exit_price}
PnL: {entry.pnl or 'N/A'}
PnL %: {entry.pnl_percent or 'N/A'}%"""

    if review_type == 'pre-trade':
        prompt = f"""Review this planned trade BEFORE execution:
{trade_info}

Provide:
1. Setup quality assessment (1-5 stars)
2. Risk evaluation — is the stop-loss well-placed?
3. R:R ratio assessment
4. Key things to watch before entering
5. Potential pitfalls"""
    else:
        prompt = f"""Review this completed trade:
{trade_info}

Provide:
1. Trade execution quality (1-5 stars)
2. What went well
3. What could be improved
4. Key lessons learned
5. Suggestions for future similar setups"""

    try:
        ai_result = _run_async(chat_completion(
            messages=[
                {"role": "system", "content": "You are a professional trading coach reviewing trades. Be constructive and educational."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=600,
        ))

        review = TradeReview(
            id=str(uuid.uuid4()),
            user_id=request.user.id,
            journal_id=entry_id,
            review_type=review_type,
            ai_analysis=ai_result.get('content', ''),
            user_notes=data.get('userNotes'),
            rating=data.get('rating'),
            lessons_learned=data.get('lessonsLearned'),
        )
        db.session.add(review)
        db.session.commit()

        return jsonify(review.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@chart_analysis_bp.route('/journal/stats', methods=['GET'])
@auth_required
def get_journal_stats():
    """Get trade journal statistics for the authenticated user"""
    user_id = request.user.id

    total = TradeJournal.query.filter_by(user_id=user_id).count()
    closed = TradeJournal.query.filter_by(user_id=user_id, status='closed')
    closed_count = closed.count()

    wins = closed.filter(TradeJournal.pnl > 0).count()
    losses = closed.filter(TradeJournal.pnl < 0).count()
    breakeven = closed.filter(TradeJournal.pnl == 0).count()

    avg_pnl = db.session.query(func.avg(TradeJournal.pnl)).filter(
        TradeJournal.user_id == user_id, TradeJournal.status == 'closed'
    ).scalar()

    total_pnl = db.session.query(func.sum(TradeJournal.pnl)).filter(
        TradeJournal.user_id == user_id, TradeJournal.status == 'closed'
    ).scalar()

    best_trade = db.session.query(func.max(TradeJournal.pnl)).filter(
        TradeJournal.user_id == user_id, TradeJournal.status == 'closed'
    ).scalar()

    worst_trade = db.session.query(func.min(TradeJournal.pnl)).filter(
        TradeJournal.user_id == user_id, TradeJournal.status == 'closed'
    ).scalar()

    active = TradeJournal.query.filter_by(user_id=user_id, status='active').count()
    planned = TradeJournal.query.filter_by(user_id=user_id, status='planned').count()

    return jsonify({
        'totalTrades': total,
        'closedTrades': closed_count,
        'activeTrades': active,
        'plannedTrades': planned,
        'wins': wins,
        'losses': losses,
        'breakeven': breakeven,
        'winRate': round(wins / closed_count * 100, 1) if closed_count else 0,
        'avgPnl': round(float(avg_pnl), 2) if avg_pnl else 0,
        'totalPnl': round(float(total_pnl), 2) if total_pnl else 0,
        'bestTrade': round(float(best_trade), 2) if best_trade else 0,
        'worstTrade': round(float(worst_trade), 2) if worst_trade else 0,
    })
