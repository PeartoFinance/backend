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
