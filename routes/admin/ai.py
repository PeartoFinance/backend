"""
Admin AI Features Routes
Manage AI agent runs and content generation
"""
import json
import uuid
from datetime import datetime
from flask import Blueprint, jsonify, request
from models import db, AgentRun, AIGenerationRun, AIPostDraft, AuditEvent
from ..decorators import admin_required

ai_bp = Blueprint('admin_ai', __name__, url_prefix='/ai')


def log_audit(action, entity, entity_id, meta=None):
    try:
        audit = AuditEvent(
            id=str(uuid.uuid4()),
            actor='admin',
            action=action,
            entity=entity,
            entityId=str(entity_id),
            meta=json.dumps(meta) if meta else None
        )
        db.session.add(audit)
    except Exception as e:
        print(f"Audit log failed: {e}")


# ============================================================================
# AGENT RUNS
# ============================================================================

@ai_bp.route('/agent-runs', methods=['GET'])
@admin_required
def get_agent_runs():
    """List all AI agent runs"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')

        query = AgentRun.query

        if status:
            query = query.filter_by(status=status)

        runs = query.order_by(AgentRun.createdAt.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return jsonify({
            'runs': [{
                'id': r.id,
                'topic': r.topic,
                'symbols': r.symbols,
                'status': r.status,
                'articleId': r.articleId,
                'error': r.error,
                'createdAt': r.createdAt.isoformat() if r.createdAt else None,
                'updatedAt': r.updatedAt.isoformat() if r.updatedAt else None,
            } for r in runs.items],
            'total': runs.total,
            'pages': runs.pages,
            'currentPage': page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@ai_bp.route('/agent-runs/<run_id>', methods=['GET'])
@admin_required
def get_agent_run(run_id):
    """Get single agent run details"""
    try:
        r = AgentRun.query.get_or_404(run_id)

        return jsonify({
            'id': r.id,
            'topic': r.topic,
            'symbols': r.symbols,
            'status': r.status,
            'steps': json.loads(r.steps) if r.steps else [],
            'articleId': r.articleId,
            'error': r.error,
            'createdAt': r.createdAt.isoformat() if r.createdAt else None,
            'updatedAt': r.updatedAt.isoformat() if r.updatedAt else None,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@ai_bp.route('/agent-runs', methods=['POST'])
@admin_required
def create_agent_run():
    """Create a new AI agent run"""
    try:
        data = request.get_json()

        if not data.get('topic'):
            return jsonify({'error': 'Topic is required'}), 400

        run_id = str(uuid.uuid4())

        run = AgentRun(
            id=run_id,
            topic=data['topic'],
            symbols=data.get('symbols', ''),
            status='pending',
            steps='[]',
            createdAt=datetime.utcnow(),
            updatedAt=datetime.utcnow()
        )

        db.session.add(run)
        db.session.commit()

        log_audit('AGENT_RUN_CREATE', 'agent_run', run_id, {'topic': data['topic']})

        # TODO: Actually trigger the AI agent here
        # from services.ai_agent import run_agent
        # run_agent.delay(run_id)

        return jsonify({'ok': True, 'id': run_id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@ai_bp.route('/agent-runs/<run_id>/retry', methods=['POST'])
@admin_required
def retry_agent_run(run_id):
    """Retry a failed agent run"""
    try:
        run = AgentRun.query.get_or_404(run_id)

        if run.status not in ['failed', 'error']:
            return jsonify({'error': 'Can only retry failed runs'}), 400

        run.status = 'pending'
        run.error = None
        run.updatedAt = datetime.utcnow()

        db.session.commit()

        log_audit('AGENT_RUN_RETRY', 'agent_run', run_id)

        return jsonify({'ok': True, 'message': 'Agent run queued for retry'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============================================================================
# CONTENT GENERATION / DRAFTS
# ============================================================================

@ai_bp.route('/drafts', methods=['GET'])
@admin_required
def get_drafts():
    """List all AI content drafts"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        drafts = AIPostDraft.query.order_by(AIPostDraft.createdAt.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return jsonify({
            'drafts': [{
                'id': d.id,
                'topic': d.topic,
                'outline': d.outline[:200] + '...' if len(d.outline) > 200 else d.outline,
                'createdAt': d.createdAt.isoformat() if d.createdAt else None,
            } for d in drafts.items],
            'total': drafts.total,
            'pages': drafts.pages,
            'currentPage': page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@ai_bp.route('/drafts/<draft_id>', methods=['GET'])
@admin_required
def get_draft(draft_id):
    """Get full draft content"""
    try:
        d = AIPostDraft.query.get_or_404(draft_id)

        return jsonify({
            'id': d.id,
            'topic': d.topic,
            'outline': d.outline,
            'draft': d.draft,
            'createdAt': d.createdAt.isoformat() if d.createdAt else None,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@ai_bp.route('/drafts', methods=['POST'])
@admin_required
def create_draft():
    """Create/generate a new AI draft"""
    try:
        data = request.get_json()

        if not data.get('topic'):
            return jsonify({'error': 'Topic is required'}), 400

        draft_id = str(uuid.uuid4())

        draft = AIPostDraft(
            id=draft_id,
            topic=data['topic'],
            outline=data.get('outline', ''),
            draft=data.get('draft', ''),
            createdAt=datetime.utcnow()
        )

        db.session.add(draft)
        db.session.commit()

        log_audit('AI_DRAFT_CREATE', 'ai_draft', draft_id, {'topic': data['topic']})

        return jsonify({'ok': True, 'id': draft_id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@ai_bp.route('/drafts/<draft_id>', methods=['PUT'])
@admin_required
def update_draft(draft_id):
    """Update a draft"""
    try:
        draft = AIPostDraft.query.get_or_404(draft_id)
        data = request.get_json()

        if 'topic' in data:
            draft.topic = data['topic']
        if 'outline' in data:
            draft.outline = data['outline']
        if 'draft' in data:
            draft.draft = data['draft']

        db.session.commit()
        log_audit('AI_DRAFT_UPDATE', 'ai_draft', draft_id)

        return jsonify({'ok': True, 'message': 'Draft updated'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@ai_bp.route('/drafts/<draft_id>', methods=['DELETE'])
@admin_required
def delete_draft(draft_id):
    """Delete a draft"""
    try:
        draft = AIPostDraft.query.get_or_404(draft_id)

        db.session.delete(draft)
        db.session.commit()

        log_audit('AI_DRAFT_DELETE', 'ai_draft', draft_id)

        return jsonify({'ok': True, 'message': 'Draft deleted'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============================================================================
# STATS
# ============================================================================

@ai_bp.route('/stats', methods=['GET'])
@admin_required
def get_ai_stats():
    """Get AI feature statistics"""
    try:
        total_runs = AgentRun.query.count()
        pending_runs = AgentRun.query.filter_by(status='pending').count()
        running_runs = AgentRun.query.filter_by(status='running').count()
        completed_runs = AgentRun.query.filter_by(status='completed').count()
        failed_runs = AgentRun.query.filter(AgentRun.status.in_(['failed', 'error'])).count()

        total_drafts = AIPostDraft.query.count()

        return jsonify({
            'agentRuns': {
                'total': total_runs,
                'pending': pending_runs,
                'running': running_runs,
                'completed': completed_runs,
                'failed': failed_runs,
            },
            'drafts': {
                'total': total_drafts,
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# AI CONTENT GENERATION FOR ADMIN FORMS
# ============================================================================

@ai_bp.route('/generate', methods=['POST'])
@admin_required
def generate_content():
    """Generate AI content for various admin forms"""
    import asyncio
    from services.ai_service import ai_service
    
    data = request.get_json() or {}
    content_type = data.get('type', 'article')
    prompt = data.get('prompt', '')
    context = data.get('context', {})
    
    if not prompt:
        return jsonify({'error': 'Prompt is required'}), 400
    
    prompts = {
        'article': f"""You are a financial content writer. Generate a professional article about: {prompt}
Write with: title, introduction, 3-4 sections with ## headers, conclusion. 500-800 words.""",
        'product_description': f"""Write a compelling product description for: {prompt}
Include key features, benefits, target audience. 150-250 words.""",
        'help_article': f"""Write help documentation for: {prompt}
Include intro, steps if applicable, tips. User-friendly, 300-500 words.""",
        'email': f"""Write a professional email for: {prompt}
Include subject line (prefix Subject:), greeting, body, CTA.""",
        'news': f"""Write a financial news article about: {prompt}
Include headline, lead, context, implications. 400-600 words.""",
        'outline': f"""Create content outline for: {prompt}
Provide title, 4-6 sections with sub-points.""",
        'rewrite': f"""Rewrite to be more engaging and professional: {prompt}""",
        'summary': f"""Summarize in 2-3 paragraphs: {prompt}""",
    }
    
    system_prompt = prompts.get(content_type, prompts['article'])
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(
            ai_service.chat(system_prompt, {'page_type': 'admin'}, {'max_tokens': 1500})
        )
        log_audit('AI_GENERATE', 'ai_content', content_type, {'prompt': prompt[:100]})
        return jsonify({'ok': True, 'content': result.get('response', ''), 'type': content_type})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        loop.close()


@ai_bp.route('/enhance', methods=['POST'])
@admin_required
def enhance_content():
    """Enhance/improve existing content"""
    import asyncio
    from services.ai_service import ai_service
    
    data = request.get_json() or {}
    content = data.get('content', '')
    action = data.get('action', 'improve')
    tone = data.get('tone', 'professional')
    
    if not content:
        return jsonify({'error': 'Content is required'}), 400
    
    actions = {
        'improve': f"Improve and polish while maintaining meaning:\n\n{content}",
        'expand': f"Expand with more details:\n\n{content}",
        'shorten': f"Make more concise:\n\n{content}",
        'proofread': f"Fix grammar/spelling:\n\n{content}",
        'tone': f"Rewrite in {tone} tone:\n\n{content}",
    }
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(
            ai_service.chat(actions.get(action, actions['improve']), {'page_type': 'admin'}, {'max_tokens': 1000})
        )
        return jsonify({'ok': True, 'content': result.get('response', ''), 'action': action})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        loop.close()


@ai_bp.route('/analyze-content', methods=['POST'])
@admin_required
def analyze_content():
    """Analyze content for improvements"""
    import asyncio
    from services.ai_service import ai_service
    
    data = request.get_json() or {}
    content = data.get('content', '')
    
    if not content:
        return jsonify({'error': 'Content is required'}), 400
    
    prompt = f"""Analyze and provide: quality score (1-10), readability, 3-5 improvements, SEO tips.

Content: {content[:2000]}"""
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(ai_service.chat(prompt, {'page_type': 'admin'}, {'max_tokens': 600}))
        return jsonify({'ok': True, 'analysis': result.get('response', '')})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        loop.close()


# ============================================================================
# BOOYAH AI PREDICTION
# ============================================================================

@ai_bp.route('/booyah/predict', methods=['POST'])
@admin_required
def booyah_predict():
    """
    Generate AI-powered stock/crypto prediction.
    Gathers market data, analyst forecasts, and news,
    then sends to AI for comprehensive prediction analysis.
    Results are cached for 30 minutes per symbol+timeframe.
    """
    import asyncio
    from services.ai_service import ai_service
    from models import MarketData, News
    from extensions import cache

    data = request.get_json() or {}
    symbol = (data.get('symbol') or '').strip().upper()
    timeframe = data.get('timeframe', '1month')  # 1week, 1month, 3months, 6months, 1year

    if not symbol:
        return jsonify({'error': 'Symbol is required'}), 400

    # Check cache first
    cache_key = f"booyah_predict:{symbol}:{timeframe}"
    cached = cache.get(cache_key)
    if cached:
        cached['cached'] = True
        return jsonify(cached)

    try:
        # 1. Fetch market data
        stock = MarketData.query.filter(
            MarketData.symbol == symbol
        ).first()

        if not stock:
            return jsonify({'error': f'Symbol {symbol} not found in database. Import it first from Market Data.'}), 404

        market_data = {
            'symbol': stock.symbol,
            'name': stock.name,
            'price': float(stock.price) if stock.price else 0,
            'change': float(stock.change) if stock.change else 0,
            'changePercent': float(stock.change_percent) if stock.change_percent else 0,
            'volume': stock.volume,
            'marketCap': stock.market_cap,
            'peRatio': float(stock.pe_ratio) if stock.pe_ratio else None,
            'eps': float(stock.eps) if stock.eps else None,
            'beta': float(stock.beta) if stock.beta else None,
            'high52w': float(stock._52_week_high) if stock._52_week_high else None,
            'low52w': float(stock._52_week_low) if stock._52_week_low else None,
            'dividendYield': float(stock.dividend_yield) if stock.dividend_yield else None,
            'sector': stock.sector,
            'industry': stock.industry,
            'assetType': stock.asset_type,
        }

        # 2. Fetch analyst forecasts if available
        forecast_data = {}
        try:
            from models.market import AnalystRecommendation
            rec = AnalystRecommendation.query.filter_by(symbol=symbol).order_by(
                AnalystRecommendation.date.desc()
            ).first()
            if rec:
                forecast_data = {
                    'targetHigh': float(rec.target_high) if rec.target_high else None,
                    'targetLow': float(rec.target_low) if rec.target_low else None,
                    'targetMean': float(rec.target_mean) if rec.target_mean else None,
                    'strongBuy': rec.strong_buy,
                    'buy': rec.buy,
                    'hold': rec.hold,
                    'sell': rec.sell,
                    'strongSell': rec.strong_sell,
                    'latestFirm': rec.firm,
                    'latestAction': rec.action,
                    'latestGrade': rec.to_grade,
                }
        except Exception:
            pass

        # 3. Fetch recent news
        recent_news = []
        try:
            news_items = News.query.filter(
                News.title.ilike(f'%{symbol}%') | News.title.ilike(f'%{stock.name}%')
            ).order_by(News.published_at.desc()).limit(5).all()
            recent_news = [
                {'title': n.title, 'source': n.source, 'date': n.published_at.isoformat() if n.published_at else None}
                for n in news_items
            ]
        except Exception:
            pass

        # 4. Build comprehensive AI prompt
        prompt = f"""You are Pearto AI's Booyah Prediction Engine. Analyze {symbol} ({stock.name}) and provide a STRUCTURED prediction.

MARKET DATA:
- Current Price: ${market_data['price']:.2f}
- Change Today: {market_data['changePercent']:.2f}%
- Volume: {market_data['volume'] or 'N/A'}
- Market Cap: {market_data['marketCap'] or 'N/A'}
- P/E Ratio: {market_data['peRatio'] or 'N/A'}
- EPS: {market_data['eps'] or 'N/A'}
- Beta: {market_data['beta'] or 'N/A'}
- 52W High: {market_data['high52w'] or 'N/A'}
- 52W Low: {market_data['low52w'] or 'N/A'}
- Sector: {market_data['sector'] or 'N/A'}
- Asset Type: {market_data['assetType'] or 'stock'}

ANALYST DATA: {json.dumps(forecast_data) if forecast_data else 'Not available'}

RECENT NEWS: {json.dumps(recent_news) if recent_news else 'No recent news'}

TIMEFRAME: {timeframe}

Respond ONLY with valid JSON (no markdown, no code blocks). Use this exact structure:
{{
    "signal": "STRONG_BUY" or "BUY" or "HOLD" or "SELL" or "STRONG_SELL",
    "confidence": 0-100,
    "sentiment": "BULLISH" or "BEARISH" or "NEUTRAL",
    "sentimentScore": -100 to 100,
    "riskLevel": "LOW" or "MEDIUM" or "HIGH" or "VERY_HIGH",
    "riskScore": 0-100,
    "priceTargets": {{
        "shortTerm": {{"price": number, "label": "1 Week"}},
        "midTerm": {{"price": number, "label": "1 Month"}},
        "longTerm": {{"price": number, "label": "3 Months"}}
    }},
    "technicalIndicators": [
        {{"name": "RSI", "value": "number or text", "signal": "BUY" or "SELL" or "NEUTRAL"}},
        {{"name": "MACD", "value": "text", "signal": "BUY" or "SELL" or "NEUTRAL"}},
        {{"name": "Moving Avg (50)", "value": "text", "signal": "BUY" or "SELL" or "NEUTRAL"}},
        {{"name": "Moving Avg (200)", "value": "text", "signal": "BUY" or "SELL" or "NEUTRAL"}},
        {{"name": "Bollinger Bands", "value": "text", "signal": "BUY" or "SELL" or "NEUTRAL"}}
    ],
    "keyFactors": [
        {{"factor": "short description", "impact": "POSITIVE" or "NEGATIVE" or "NEUTRAL"}}
    ],
    "summary": "2-3 sentence prediction summary",
    "detailedAnalysis": "4-6 sentence detailed analysis with reasoning"
}}"""

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                ai_service.chat(prompt, {'page_type': 'prediction'}, {'max_tokens': 1500, 'temperature': 0.3})
            )
            ai_response = result.get('response', '')

            # Parse JSON from AI response
            prediction = None
            try:
                # Try direct parse
                prediction = json.loads(ai_response)
            except json.JSONDecodeError:
                # Try extracting JSON from response
                import re
                json_match = re.search(r'\{[\s\S]*\}', ai_response)
                if json_match:
                    try:
                        prediction = json.loads(json_match.group())
                    except json.JSONDecodeError:
                        pass

            if not prediction:
                return jsonify({
                    'error': 'AI returned invalid prediction format',
                    'rawResponse': ai_response[:500]
                }), 500

            # Add metadata
            prediction['symbol'] = symbol
            prediction['name'] = stock.name
            prediction['assetType'] = stock.asset_type
            prediction['currentPrice'] = market_data['price']
            prediction['marketData'] = market_data
            prediction['analystData'] = forecast_data
            prediction['recentNews'] = recent_news
            prediction['timeframe'] = timeframe
            prediction['generatedAt'] = datetime.utcnow().isoformat()
            prediction['provider'] = result.get('provider', 'SathiAI')

            log_audit('BOOYAH_PREDICT', 'prediction', symbol, {
                'signal': prediction.get('signal'),
                'confidence': prediction.get('confidence'),
                'timeframe': timeframe
            })

            # Cache successful prediction for 30 minutes
            cache.set(cache_key, prediction, timeout=1800)

            return jsonify(prediction)

        finally:
            loop.close()

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@ai_bp.route('/booyah/quick-scan', methods=['POST'])
@admin_required
def booyah_quick_scan():
    """
    Quick AI scan of multiple symbols for rapid signal overview.
    Results cached for 15 minutes per symbol set.
    """
    import asyncio
    from services.ai_service import ai_service
    from models import MarketData
    from extensions import cache

    data = request.get_json() or {}
    symbols = data.get('symbols', [])

    if not symbols or len(symbols) > 20:
        return jsonify({'error': 'Provide 1-20 symbols'}), 400

    # Cache key based on sorted symbols
    sorted_syms = sorted([s.strip().upper() for s in symbols])
    cache_key = f"booyah_scan:{'_'.join(sorted_syms)}"
    cached = cache.get(cache_key)
    if cached:
        cached['cached'] = True
        return jsonify(cached)

    results = []
    for sym in symbols:
        sym = sym.strip().upper()
        stock = MarketData.query.filter(MarketData.symbol == sym).first()
        if stock:
            results.append({
                'symbol': stock.symbol,
                'name': stock.name,
                'price': float(stock.price) if stock.price else 0,
                'change': float(stock.change) if stock.change else 0,
                'changePercent': float(stock.change_percent) if stock.change_percent else 0,
                'volume': stock.volume,
                'marketCap': stock.market_cap,
                'sector': stock.sector,
            })

    if not results:
        return jsonify({'error': 'No matching symbols found'}), 404

    # Build AI prompt for quick scan
    symbols_text = '\n'.join([
        f"- {r['symbol']}: ${r['price']:.2f} ({r['changePercent']:+.2f}%), Vol: {r['volume'] or 'N/A'}"
        for r in results
    ])

    prompt = f"""Quick market scan. For each symbol, give a 1-word signal and confidence.

{symbols_text}

Respond ONLY with valid JSON array (no markdown):
[{{"symbol": "AAPL", "signal": "BUY", "confidence": 75, "reason": "short reason"}}]"""

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(
            ai_service.chat(prompt, {'page_type': 'prediction'}, {'max_tokens': 800, 'temperature': 0.3})
        )
        ai_response = result.get('response', '')

        try:
            import re
            json_match = re.search(r'\[[\s\S]*\]', ai_response)
            if json_match:
                signals = json.loads(json_match.group())
            else:
                signals = json.loads(ai_response)
        except json.JSONDecodeError:
            signals = []

        # Merge AI signals with market data
        for r in results:
            ai_sig = next((s for s in signals if s.get('symbol', '').upper() == r['symbol']), None)
            if ai_sig:
                r['signal'] = ai_sig.get('signal', 'HOLD')
                r['confidence'] = ai_sig.get('confidence', 50)
                r['reason'] = ai_sig.get('reason', '')
            else:
                r['signal'] = 'HOLD'
                r['confidence'] = 50
                r['reason'] = 'Insufficient data'

        response_data = {'results': results, 'generatedAt': datetime.utcnow().isoformat()}
        cache.set(cache_key, response_data, timeout=900)  # 15 min
        return jsonify(response_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        loop.close()


# ============================================================================
# AI PROVIDER MANAGEMENT
# ============================================================================

@ai_bp.route('/provider', methods=['GET'])
@admin_required
def get_ai_provider():
    """Get current AI provider configuration"""
    from services.ai_provider import get_active_provider_name
    from services.settings_service import get_setting_secure
    import os

    provider = get_active_provider_name()
    model = get_setting_secure('AI_MODEL', os.getenv('AI_MODEL', 'gpt-4'))
    base_url = get_setting_secure('SATHI_AI_BASE_URL', os.getenv('OPENAI_BASE_URL', ''))

    # Check if API key is set (don't return actual key)
    api_key = get_setting_secure('SATHI_AI_API_KEY', os.getenv('OPENAI_API_KEY', ''))
    has_api_key = bool(api_key and len(api_key) > 5)

    return jsonify({
        'provider': provider,
        'model': model,
        'baseUrl': base_url if provider == 'openai' else None,
        'hasApiKey': has_api_key,
        'availableProviders': ['openai', 'g4f'],
    })


@ai_bp.route('/provider', methods=['PUT'])
@admin_required
def update_ai_provider():
    """Switch AI provider or update AI settings"""
    from models.settings import Settings
    from services.settings_service import get_setting_secure

    data = request.get_json() or {}
    provider = data.get('provider')
    model = data.get('model')
    base_url = data.get('baseUrl')
    api_key = data.get('apiKey')

    if provider and provider not in ('openai', 'g4f'):
        return jsonify({'error': 'Invalid provider. Use "openai" or "g4f".'}), 400

    updated = []

    def _upsert_setting(key, value, category='ai', desc=''):
        setting = Settings.query.filter_by(key=key).first()
        if setting:
            setting.value = value
            setting.updated_at = datetime.utcnow()
        else:
            setting = Settings(
                id=str(uuid.uuid4()),
                key=key,
                value=value,
                type='string',
                category=category,
                description=desc,
                is_public=False,
                is_encrypted=False,
            )
            db.session.add(setting)
        updated.append(key)

    try:
        if provider:
            _upsert_setting('AI_PROVIDER', provider, desc='Active AI provider (openai or g4f)')
        if model:
            _upsert_setting('AI_MODEL', model, desc='AI model name')
        if base_url is not None:
            _upsert_setting('SATHI_AI_BASE_URL', base_url, desc='OpenAI-compatible API base URL')
        if api_key is not None:
            _upsert_setting('SATHI_AI_API_KEY', api_key, desc='OpenAI-compatible API key')

        db.session.commit()

        log_audit('AI_PROVIDER_UPDATE', 'settings', 'ai', {
            'provider': provider,
            'model': model,
            'updated_keys': updated,
        })

        return jsonify({
            'ok': True,
            'message': f'AI settings updated: {", ".join(updated)}',
            'provider': provider or get_setting_secure('AI_PROVIDER', 'openai'),
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@ai_bp.route('/provider/test', methods=['POST'])
@admin_required
def test_ai_provider():
    """Test the active (or specified) AI provider with a quick chat"""
    import asyncio
    from services.ai_provider import chat_completion, health_check

    data = request.get_json() or {}
    provider_name = data.get('provider')  # optional override
    test_message = data.get('message', 'Say hello in one sentence.')

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        # Health check
        status = loop.run_until_complete(health_check(provider_name))

        # Quick chat test
        result = loop.run_until_complete(chat_completion(
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Answer briefly."},
                {"role": "user", "content": test_message},
            ],
            max_tokens=100,
            provider_name=provider_name,
        ))

        return jsonify({
            'ok': result.get('success', False),
            'health': status,
            'response': result.get('content', ''),
            'provider': result.get('provider', 'unknown'),
            'model': result.get('model', ''),
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500
    finally:
        loop.close()
