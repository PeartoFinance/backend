"""
Admin News Management Routes
CRUD for /api/admin/news
"""
from flask import Blueprint, jsonify, request
from datetime import datetime
from ..decorators import admin_required
from models import db, NewsItem

news_bp = Blueprint('admin_news', __name__)


@news_bp.route('/news', methods=['GET'])
@admin_required
def get_news():
    """List all news articles with filters"""
    try:
        country = getattr(request, 'user_country', 'US')
        is_global = not country or country == 'GLOBAL'
        
        status = request.args.get('status')  # draft, published, archived
        source_type = request.args.get('source_type')  # rss, admin
        category = request.args.get('category')
        search = request.args.get('search', '').strip()
        limit = min(int(request.args.get('limit', 100)), 500)
        offset = int(request.args.get('offset', 0))
        
        # Base query
        query = NewsItem.query
        
        # Apply country filter if not in "All Countries" mode
        if not is_global:
            query = query.filter(
                (NewsItem.country_code == country) | 
                (NewsItem.country_code == 'GLOBAL') |
                (NewsItem.country_code == None)
            )
        
        # Apply filters
        if status and status != 'all':
            query = query.filter(NewsItem.curated_status == status)
        
        if source_type and source_type != 'all':
            query = query.filter(NewsItem.source_type == source_type)
        
        if category:
            query = query.filter(NewsItem.category == category)
        
        if search:
            query = query.filter(NewsItem.title.ilike(f'%{search}%'))
            
        # Date filtering
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if start_date:
            try:
                start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                query = query.filter(NewsItem.published_at >= start)
            except ValueError:
                pass
                
        if end_date:
            try:
                # Add 1 day to end_date to include the full day if it's just a date string
                end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                if len(end_date) <= 10: # YYYY-MM-DD
                    end = end.replace(hour=23, minute=59, second=59)
                query = query.filter(NewsItem.published_at <= end)
            except ValueError:
                pass
        
        # Get total count
        total = query.count()
        
        # Get paginated results
        articles = query.order_by(NewsItem.published_at.desc()).offset(offset).limit(limit).all()
        
        return jsonify({
            'news': [a.to_dict() for a in articles],
            'total': total,
            'limit': limit,
            'offset': offset
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@news_bp.route('/news/<int:news_id>', methods=['GET'])
@admin_required
def get_news_item(news_id):
    """Get single news article"""
    try:
        article = NewsItem.query.get_or_404(news_id)
        return jsonify(article.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@news_bp.route('/news', methods=['POST'])
@admin_required
def create_news():
    """Create news article"""
    try:
        data = request.get_json()
        article = NewsItem(
            title=data.get('title'),
            summary=data.get('summary'),
            source=data.get('source'),
            category=data.get('category'),
            image=data.get('image'),
            link=data.get('link'),
            slug=data.get('slug'),
            author=data.get('author'),
            full_content=data.get('full_content'),
            is_published=data.get('is_published', False),
            featured=data.get('featured', False),
            published_at=datetime.utcnow() if data.get('is_published') else None,
            created_at=datetime.utcnow(),
            country_code=data.get('country_code', getattr(request, 'user_country', 'US'))
        )
        db.session.add(article)
        db.session.commit()
        return jsonify({'ok': True, 'id': article.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@news_bp.route('/news/<int:news_id>', methods=['PUT'])
@admin_required
def update_news(news_id):
    """Update news article"""
    try:
        article = NewsItem.query.get_or_404(news_id)
        data = request.get_json()
        
        if 'title' in data:
            article.title = data['title']
        if 'summary' in data:
            article.summary = data['summary']
        if 'source' in data:
            article.source = data['source']
        if 'category' in data:
            article.category = data['category']
        if 'image' in data:
            article.image = data['image']
        if 'link' in data:
            article.link = data['link']
        if 'slug' in data:
            article.slug = data['slug']
        if 'author' in data:
            article.author = data['author']
        if 'full_content' in data:
            article.full_content = data['full_content']
        if 'is_published' in data:
            article.is_published = data['is_published']
            if data['is_published'] and not article.published_at:
                article.published_at = datetime.utcnow()
        if 'featured' in data:
            article.featured = data['featured']
        if 'related_symbol' in data:
            article.related_symbol = data['related_symbol'].upper() if data['related_symbol'] else None
        
        article.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'ok': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@news_bp.route('/news/<int:news_id>', methods=['DELETE'])
@admin_required
def delete_news(news_id):
    """Delete news article"""
    try:
        article = NewsItem.query.get_or_404(news_id)
        db.session.delete(article)
        db.session.commit()
        return jsonify({'ok': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@news_bp.route('/news/fetch', methods=['POST'])
@admin_required
def fetch_news_from_sources():
    """Fetch news from RSS and external sources"""
    try:
        from services.news_source_manager import news_source_manager
        results = news_source_manager.pull_all_sources()
        return jsonify({
            'success': True,
            'fetched': len(results),
            'message': f'Fetched {len(results)} news items'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@news_bp.route('/news/import-company', methods=['POST'])
@admin_required
def import_company_news():
    """Import news for a specific company/symbol from Yahoo Finance"""
    try:
        from handlers.market_data.stock_handler import sync_stock_news
        
        data = request.get_json()
        symbol = data.get('symbol', '').strip()
        
        if not symbol:
            return jsonify({'error': 'Symbol is required'}), 400
            
        result = sync_stock_news(symbol)
        
        if result.get('status') == 'error':
            return jsonify({'error': result.get('message')}), 500
            
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@news_bp.route('/news/external-search', methods=['POST'])
@admin_required
def search_external_news():
    """Search for news from external sources (preview only)"""
    try:
        from handlers.market_data.stock_handler import fetch_stock_news_preview
        
        data = request.get_json()
        symbol = data.get('symbol', '').strip()
        
        if not symbol:
            return jsonify({'error': 'Symbol is required'}), 400
            
        result = fetch_stock_news_preview(symbol)
        
        if result.get('status') == 'error':
            return jsonify({'error': result.get('message')}), 500
            
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@news_bp.route('/news/import-bulk', methods=['POST'])
@admin_required
def import_bulk_news():
    """Import specific selected news items"""
    try:
        import hashlib
        import re
        
        data = request.get_json()
        items = data.get('items', [])
        
        if not items:
            return jsonify({'error': 'No items provided'}), 400
            
        imported = 0
        
        for item in items:
            title = item.get('title')
            link = item.get('canonical_url')
            
            if not title or not link:
                continue
                
            # Generate hash
            item_hash = hashlib.sha256(f"{link}|{title}".encode('utf-8')).hexdigest()
            
            # Check existing
            if NewsItem.query.filter_by(hash=item_hash).first():
                continue
                
            # Create slug
            slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')[:100]
            if NewsItem.query.filter_by(slug=slug).first():
                slug = f"{slug}-{int(datetime.utcnow().timestamp())}"
            
            # Parse date
            pub_date = datetime.utcnow()
            if item.get('published_at'):
                try:
                    pub_date = datetime.fromisoformat(item.get('published_at').replace('Z', '+00:00'))
                except:
                    pass
            
            news_item = NewsItem(
                title=title,
                summary=item.get('summary'),
                canonical_url=link,
                source=item.get('source', 'External'),
                published_at=pub_date,
                hash=item_hash,
                slug=slug,
                related_symbol=item.get('related_symbol'),
                curated_status='published',
                source_type='yfinance',
                image=item.get('image'),
                created_at=datetime.utcnow()
            )
            db.session.add(news_item)
            imported += 1
            
        db.session.commit()
        return jsonify({'success': True, 'imported': imported})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@news_bp.route('/news/create', methods=['POST'])
@admin_required
def create_admin_article():
    """Create a new admin-written article"""
    try:
        data = request.get_json()
        title = data.get('title', '').strip()
        
        if not title:
            return jsonify({'error': 'Title is required'}), 400
        
        # Generate slug from title
        import re
        base_slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')[:100]
        
        # Check for slug uniqueness
        slug = base_slug
        counter = 1
        while NewsItem.query.filter_by(slug=slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        country = data.get('country_code', getattr(request, 'user_country', 'US'))
        now = datetime.utcnow()
        
        article = NewsItem(
            title=title,
            summary=data.get('summary', ''),
            full_content=data.get('full_content', ''),
            author=data.get('author', 'Admin'),
            image=data.get('image'),
            category=data.get('category', 'general'),
            source_type='admin',
            curated_status='published' if data.get('published') else 'draft',
            featured=data.get('featured', False),
            slug=slug,
            country_code=country,
            published_at=now if data.get('published') else None,
            related_symbol=data.get('related_symbol').upper() if data.get('related_symbol') else None,
            created_at=now,
            updated_at=now
        )
        
        db.session.add(article)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'slug': slug,
            'id': article.id,
            'message': 'Article created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@news_bp.route('/news/bulk-action', methods=['POST'])
@admin_required
def bulk_action_news():
    """Bulk publish/archive/delete news items"""
    try:
        data = request.get_json()
        action = data.get('action')
        ids = data.get('ids', [])
        
        if not ids or not isinstance(ids, list):
            return jsonify({'error': 'Invalid ids array'}), 400
        
        if action == 'publish':
            NewsItem.query.filter(NewsItem.id.in_(ids)).update(
                {'curated_status': 'published'}, synchronize_session=False
            )
            db.session.commit()
            return jsonify({'success': True, 'message': f'Published {len(ids)} items'})
            
        elif action == 'archive':
            NewsItem.query.filter(NewsItem.id.in_(ids)).update(
                {'curated_status': 'archived'}, synchronize_session=False
            )
            db.session.commit()
            return jsonify({'success': True, 'message': f'Archived {len(ids)} items'})
            
        elif action == 'delete':
            NewsItem.query.filter(NewsItem.id.in_(ids)).delete(synchronize_session=False)
            db.session.commit()
            return jsonify({'success': True, 'message': f'Deleted {len(ids)} items'})
            
        else:
            return jsonify({'error': 'Invalid action'}), 400
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

