"""
Admin Sports Settings Routes
Manage sports categories, import events, and view stats
"""
from flask import Blueprint, jsonify, request
from models.media import SportsCategory, SportsEvent, db
from routes.decorators import admin_required
from datetime import datetime

sports_settings_bp = Blueprint('sports_settings', __name__, url_prefix='/api/admin/sports-settings')


# ==================== CATEGORIES ====================

@sports_settings_bp.route('/', methods=['GET'])
@admin_required
def get_sports_settings():
    """Get all sports categories with event counts"""
    try:
        categories = SportsCategory.query.order_by(SportsCategory.name).all()
        result = []
        for c in categories:
            cat_dict = c.to_dict()
            cat_dict['eventCount'] = SportsEvent.query.filter_by(sport_type=c.name).count()
            cat_dict['liveCount'] = SportsEvent.query.filter_by(sport_type=c.name, is_live=True).count()
            result.append(cat_dict)

        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@sports_settings_bp.route('/<int:id>/status', methods=['PUT'])
@admin_required
def update_sport_status(id):
    """Toggle sport active status"""
    try:
        data = request.get_json()
        is_active = data.get('isActive')

        if is_active is None:
            return jsonify({'success': False, 'error': 'isActive is required'}), 400

        category = SportsCategory.query.get(id)
        if not category:
            return jsonify({'success': False, 'error': 'Sport category not found'}), 404

        category.is_active = is_active
        db.session.commit()

        return jsonify({
            'success': True,
            'data': category.to_dict(),
            'message': f"{category.name} is now {'active' if is_active else 'inactive'}"
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== IMPORT ====================

@sports_settings_bp.route('/import', methods=['POST'])
@admin_required
def import_sports_events():
    """
    Manually trigger import of sports events from external API into DB.
    Body: { date?: "YYYY-MM-DD", sportKey?: "football" }
    """
    try:
        data = request.get_json() or {}
        date = data.get('date')
        sport_key = data.get('sportKey')

        from services.sports_import_service import SportsImportService
        stats = SportsImportService.import_events(date=date, sport_key=sport_key)

        return jsonify({
            'success': True,
            'data': stats,
            'message': stats.get('message', 'Import completed')
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@sports_settings_bp.route('/refresh-live', methods=['POST'])
@admin_required
def refresh_live_events():
    """Manually refresh live event scores"""
    try:
        from services.sports_import_service import SportsImportService
        stats = SportsImportService.refresh_live_events()
        return jsonify({
            'success': True,
            'data': stats,
            'message': f"Refreshed {stats['updated']} live events"
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@sports_settings_bp.route('/sync', methods=['POST'])
@admin_required
def sync_sports():
    """Alias for import — backwards compatible with existing admin UI"""
    try:
        from services.sports_import_service import SportsImportService
        stats = SportsImportService.import_events()
        return jsonify({
            'success': True,
            'data': stats,
            'message': stats.get('message', 'Sync completed')
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== EVENTS MANAGEMENT ====================

@sports_settings_bp.route('/events', methods=['GET'])
@admin_required
def get_events():
    """
    Get stored sports events with filters.
    Query params: sport, status, date, search, page, limit
    """
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 50, type=int)
        sport = request.args.get('sport')
        status = request.args.get('status')
        date = request.args.get('date')
        search = request.args.get('search')

        query = SportsEvent.query

        if sport and sport != 'All':
            query = query.filter(SportsEvent.sport_type == sport)
        if status and status != 'all':
            if status == 'live':
                query = query.filter(SportsEvent.is_live == True)
            else:
                query = query.filter(SportsEvent.status == status)
        if date:
            try:
                d = datetime.strptime(date, '%Y-%m-%d')
                query = query.filter(
                    db.func.date(SportsEvent.event_date) == d.date()
                )
            except ValueError:
                pass
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                db.or_(
                    SportsEvent.name.ilike(search_term),
                    SportsEvent.league.ilike(search_term),
                    SportsEvent.team_home.ilike(search_term),
                    SportsEvent.team_away.ilike(search_term),
                )
            )

        query = query.order_by(SportsEvent.event_date.desc())
        paginated = query.paginate(page=page, per_page=limit, error_out=False)

        return jsonify({
            'success': True,
            'data': [e.to_dict() for e in paginated.items],
            'total': paginated.total,
            'page': page,
            'pages': paginated.pages,
            'count': len(paginated.items)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@sports_settings_bp.route('/events', methods=['POST'])
@admin_required
def create_event():
    """Create a new sports event manually"""
    try:
        data = request.get_json() or {}

        required = ['name', 'sportType']
        for field in required:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'{field} is required'}), 400

        event_date = None
        if data.get('eventDate'):
            try:
                event_date = datetime.fromisoformat(data['eventDate'].replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                try:
                    event_date = datetime.strptime(data['eventDate'][:19], '%Y-%m-%dT%H:%M:%S')
                except Exception:
                    event_date = None

        new_event = SportsEvent(
            external_id=data.get('externalId'),
            name=data['name'],
            sport_type=data['sportType'],
            league=data.get('league', ''),
            team_home=data.get('teamHome', ''),
            team_away=data.get('teamAway', ''),
            score_home=data.get('scoreHome', '-'),
            score_away=data.get('scoreAway', '-'),
            event_date=event_date,
            venue=data.get('venue', ''),
            status=data.get('status', 'scheduled'),
            stream_url=data.get('streamUrl', ''),
            thumbnail_url=data.get('thumbnailUrl', ''),
            country_code=data.get('countryCode', ''),
            is_active=data.get('isActive', True),
            is_live=data.get('isLive', False),
        )
        db.session.add(new_event)
        db.session.commit()

        return jsonify({
            'success': True,
            'data': new_event.to_dict(),
            'message': 'Event created successfully'
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@sports_settings_bp.route('/events/<int:id>', methods=['GET'])
@admin_required
def get_single_event(id):
    """Get a single event by ID"""
    try:
        event = SportsEvent.query.get(id)
        if not event:
            return jsonify({'success': False, 'error': 'Event not found'}), 404
        return jsonify({'success': True, 'data': event.to_dict()})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@sports_settings_bp.route('/events/<int:id>', methods=['PUT'])
@admin_required
def update_event(id):
    """Update a sports event"""
    try:
        event = SportsEvent.query.get(id)
        if not event:
            return jsonify({'success': False, 'error': 'Event not found'}), 404

        data = request.get_json() or {}

        # Update all editable fields
        if 'name' in data:
            event.name = data['name']
        if 'sportType' in data:
            event.sport_type = data['sportType']
        if 'league' in data:
            event.league = data['league']
        if 'teamHome' in data:
            event.team_home = data['teamHome']
        if 'teamAway' in data:
            event.team_away = data['teamAway']
        if 'scoreHome' in data:
            event.score_home = data['scoreHome']
        if 'scoreAway' in data:
            event.score_away = data['scoreAway']
        if 'venue' in data:
            event.venue = data['venue']
        if 'status' in data:
            event.status = data['status']
        if 'streamUrl' in data:
            event.stream_url = data['streamUrl']
        if 'thumbnailUrl' in data:
            event.thumbnail_url = data['thumbnailUrl']
        if 'countryCode' in data:
            event.country_code = data['countryCode']
        if 'isActive' in data:
            event.is_active = data['isActive']
        if 'isLive' in data:
            event.is_live = data['isLive']
        if 'eventDate' in data and data['eventDate']:
            try:
                event.event_date = datetime.fromisoformat(data['eventDate'].replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                try:
                    event.event_date = datetime.strptime(data['eventDate'][:19], '%Y-%m-%dT%H:%M:%S')
                except Exception:
                    pass

        event.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'success': True,
            'data': event.to_dict(),
            'message': 'Event updated successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@sports_settings_bp.route('/events/<int:id>', methods=['DELETE'])
@admin_required
def delete_event(id):
    """Delete a sports event"""
    try:
        event = SportsEvent.query.get(id)
        if not event:
            return jsonify({'success': False, 'error': 'Event not found'}), 404

        db.session.delete(event)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Event deleted'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@sports_settings_bp.route('/events/clear', methods=['POST'])
@admin_required
def clear_events():
    """
    Clear old events from DB.
    Body: { olderThanDays?: 7, sport?: "Football" }
    """
    try:
        data = request.get_json() or {}
        days = data.get('olderThanDays', 7)
        sport = data.get('sport')

        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(days=days)

        query = SportsEvent.query.filter(SportsEvent.event_date < cutoff)
        if sport:
            query = query.filter(SportsEvent.sport_type == sport)

        count = query.delete(synchronize_session=False)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Deleted {count} events older than {days} days',
            'deletedCount': count
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== STATS ====================

@sports_settings_bp.route('/stats', methods=['GET'])
@admin_required
def get_sports_stats():
    """Get import statistics"""
    try:
        total = SportsEvent.query.count()
        live = SportsEvent.query.filter_by(is_live=True).count()
        scheduled = SportsEvent.query.filter_by(status='scheduled').count()
        completed = SportsEvent.query.filter_by(status='completed').count()

        from sqlalchemy import func
        sport_breakdown = db.session.query(
            SportsEvent.sport_type,
            func.count(SportsEvent.id)
        ).group_by(SportsEvent.sport_type).all()

        last_event = SportsEvent.query.order_by(SportsEvent.updated_at.desc()).first()
        last_import = last_event.updated_at.isoformat() if last_event and last_event.updated_at else None

        return jsonify({
            'success': True,
            'data': {
                'total': total,
                'live': live,
                'scheduled': scheduled,
                'completed': completed,
                'lastImport': last_import,
                'byType': {s: c for s, c in sport_breakdown if s}
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== SEED ====================

@sports_settings_bp.route('/seed', methods=['POST'])
@admin_required
def seed_sports_endpoint():
    """Seed sports categories directly via API"""
    try:
        sports = [
            {'name': 'Football', 'key': 'football', 'api_url': 'https://v3.football.api-sports.io', 'icon': 'Trophy', 'is_active': True},
            {'name': 'Basketball', 'key': 'basketball', 'api_url': 'https://v1.basketball.api-sports.io', 'icon': 'Dribbble', 'is_active': True},
            {'name': 'Baseball', 'key': 'baseball', 'api_url': 'https://v1.baseball.api-sports.io', 'icon': 'Baseball', 'is_active': True},
            {'name': 'Rugby', 'key': 'rugby', 'api_url': 'https://v1.rugby.api-sports.io', 'icon': 'Grab', 'is_active': True},
            {'name': 'Hockey', 'key': 'hockey', 'api_url': 'https://v1.hockey.api-sports.io', 'icon': 'Disc', 'is_active': True},
            {'name': 'AFL', 'key': 'afl', 'api_url': 'https://v1.afl.api-sports.io', 'icon': 'Activity', 'is_active': False},
            {'name': 'Formula 1', 'key': 'formula-1', 'api_url': 'https://v1.formula-1.api-sports.io', 'icon': 'Car', 'is_active': False},
            {'name': 'Handball', 'key': 'handball', 'api_url': 'https://v1.handball.api-sports.io', 'icon': 'Grab', 'is_active': True},
            {'name': 'MMA', 'key': 'mma', 'api_url': 'https://v1.mma.api-sports.io', 'icon': 'Swords', 'is_active': False},
            {'name': 'NBA', 'key': 'nba', 'api_url': 'https://v2.nba.api-sports.io', 'icon': 'Dribbble', 'is_active': True},
            {'name': 'NFL', 'key': 'nfl', 'api_url': 'https://v1.american-football.api-sports.io', 'icon': 'Shirt', 'is_active': True},
            {'name': 'Volleyball', 'key': 'volleyball', 'api_url': 'https://v1.volleyball.api-sports.io', 'icon': 'Volleyball', 'is_active': True}
        ]

        added_count = 0
        updated_count = 0

        for sport_data in sports:
            existing = SportsCategory.query.filter_by(key=sport_data['key']).first()
            if not existing:
                new_sport = SportsCategory(**sport_data)
                db.session.add(new_sport)
                added_count += 1
            else:
                existing.api_url = sport_data['api_url']
                existing.icon = sport_data['icon']
                updated_count += 1

        db.session.commit()
        return jsonify({'success': True, 'message': f'Seeding completed. Added {added_count}, updated {updated_count}.'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
