
from flask import Blueprint, jsonify, request
from extensions import cache
from datetime import datetime
from routes.decorators import auth_required

sports_bp = Blueprint('sports', __name__)


# ─── Helper: get current user from JWT ───
def _get_current_user():
    from routes.user import get_current_user
    return get_current_user()


# ─── Favorites ───

@sports_bp.route('/favorites', methods=['GET'])
@auth_required
def get_favorites():
    """Get current user's favorite/pinned sports events"""
    user = _get_current_user()
    if not user:
        return jsonify({'success': False, 'error': 'Authentication required'}), 401
    try:
        from models.media import UserFavoriteSport
        favs = UserFavoriteSport.query.filter_by(user_id=user.id).all()
        return jsonify({
            'success': True,
            'count': len(favs),
            'data': [f.to_dict() for f in favs]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@sports_bp.route('/favorites', methods=['POST'])
@auth_required
def add_favorite():
    """Add a sports event to user's favorites/pins"""
    user = _get_current_user()
    if not user:
        return jsonify({'success': False, 'error': 'Authentication required'}), 401
    try:
        from models.media import UserFavoriteSport, SportsEvent, db
        data = request.get_json() or {}
        event_id = data.get('eventId')
        if not event_id:
            return jsonify({'success': False, 'error': 'eventId is required'}), 400

        # Check event exists
        event = SportsEvent.query.get(event_id)
        if not event:
            return jsonify({'success': False, 'error': 'Event not found'}), 404

        # Check not already favorited
        existing = UserFavoriteSport.query.filter_by(user_id=user.id, event_id=event_id).first()
        if existing:
            return jsonify({'success': True, 'data': existing.to_dict(), 'message': 'Already favorited'})

        fav = UserFavoriteSport(
            user_id=user.id,
            event_id=event_id,
            notify_email=data.get('notifyEmail', True),
            notify_push=data.get('notifyPush', True)
        )
        db.session.add(fav)
        db.session.commit()
        return jsonify({'success': True, 'data': fav.to_dict()}), 201
    except Exception as e:
        from models.media import db
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@sports_bp.route('/favorites/<int:event_id>', methods=['DELETE'])
@auth_required
def remove_favorite(event_id):
    """Remove a sports event from user's favorites"""
    user = _get_current_user()
    if not user:
        return jsonify({'success': False, 'error': 'Authentication required'}), 401
    try:
        from models.media import UserFavoriteSport, db
        fav = UserFavoriteSport.query.filter_by(user_id=user.id, event_id=event_id).first()
        if not fav:
            return jsonify({'success': False, 'error': 'Favorite not found'}), 404
        db.session.delete(fav)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Removed from favorites'})
    except Exception as e:
        from models.media import db
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@sports_bp.route('/favorites/<int:event_id>/notifications', methods=['PUT'])
@auth_required
def update_favorite_notifications(event_id):
    """Update notification preferences for a favorited event"""
    user = _get_current_user()
    if not user:
        return jsonify({'success': False, 'error': 'Authentication required'}), 401
    try:
        from models.media import UserFavoriteSport, db
        fav = UserFavoriteSport.query.filter_by(user_id=user.id, event_id=event_id).first()
        if not fav:
            return jsonify({'success': False, 'error': 'Favorite not found'}), 404
        data = request.get_json() or {}
        if 'notifyEmail' in data:
            fav.notify_email = data['notifyEmail']
        if 'notifyPush' in data:
            fav.notify_push = data['notifyPush']
        db.session.commit()
        return jsonify({'success': True, 'data': fav.to_dict()})
    except Exception as e:
        from models.media import db
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@sports_bp.route('/favorites/ids', methods=['GET'])
@auth_required
def get_favorite_ids():
    """Get just the event IDs of user's favorites (lightweight for checking pin status)"""
    user = _get_current_user()
    if not user:
        return jsonify({'success': True, 'data': []})  # Return empty for unauthenticated
    try:
        from models.media import UserFavoriteSport
        favs = UserFavoriteSport.query.filter_by(user_id=user.id).all()
        return jsonify({
            'success': True,
            'data': [f.event_id for f in favs]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@sports_bp.route('/fixtures', methods=['GET'])
@cache.cached(timeout=10, query_string=True)
def get_fixtures():
    """
    Get sports events from the database.
    Query Params:
    - status: 'live', 'upcoming', 'completed', 'all' (default: 'all')
    - date: YYYY-MM-DD (optional, defaults to today)
    - sport: sport type filter (optional)
    """
    status = request.args.get('status', 'all')
    date = request.args.get('date')
    sport = request.args.get('sport')

    try:
        from models.media import SportsEvent, SportsCategory, db

        query = SportsEvent.query.filter_by(is_active=True)

        # Date filter
        if date:
            try:
                d = datetime.strptime(date, '%Y-%m-%d')
                query = query.filter(
                    db.func.date(SportsEvent.event_date) == d.date()
                )
            except ValueError:
                pass
        else:
            # Default to today
            today = datetime.now().date()
            query = query.filter(
                db.func.date(SportsEvent.event_date) == today
            )

        # Status filter
        if status == 'live':
            query = query.filter(SportsEvent.is_live == True)
        elif status == 'upcoming':
            query = query.filter(SportsEvent.status == 'scheduled')
        elif status == 'completed':
            query = query.filter(SportsEvent.status == 'completed')
        # 'all' — no status filter

        # Sport filter
        if sport and sport != 'All':
            # Match against sport_type (category name) or sport key
            cat = SportsCategory.query.filter(
                db.or_(SportsCategory.name == sport, SportsCategory.key == sport)
            ).first()
            if cat:
                query = query.filter(SportsEvent.sport_type == cat.name)
            else:
                query = query.filter(SportsEvent.sport_type == sport)

        events = query.order_by(SportsEvent.event_date.asc()).all()

        return jsonify({
            'success': True,
            'count': len(events),
            'data': [e.to_dict() for e in events]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@sports_bp.route('/events/<int:event_id>', methods=['GET'])
def get_event_detail(event_id):
    """
    Get a single sports event by ID.
    If it's a live event, refreshes from external API first.
    """
    try:
        from services.sports_import_service import SportsImportService
        event = SportsImportService.get_single_event_fresh(event_id)

        if not event:
            return jsonify({'success': False, 'error': 'Event not found'}), 404

        return jsonify({
            'success': True,
            'data': event.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@sports_bp.route('/events/batch-refresh', methods=['POST'])
def batch_refresh_events():
    """
    Batch-refresh multiple events by IDs.
    Live/scheduled events are refreshed from the external API (batched per sport);
    completed events are returned from DB as-is.
    Body: { "ids": [1, 2, 3] }
    """
    try:
        from models.media import SportsEvent as SE, SportsCategory, db
        from services.api_sports_service import APISportsService

        body = request.get_json(silent=True) or {}
        event_ids = body.get('ids', [])
        if not event_ids or not isinstance(event_ids, list):
            return jsonify({'success': False, 'error': 'ids array required'}), 400

        # Limit to 20 to avoid abuse
        event_ids = [int(eid) for eid in event_ids[:20]]

        # 1. Load all requested events from DB in one query
        events = SE.query.filter(SE.id.in_(event_ids)).all()
        event_map = {e.id: e for e in events}

        # 2. Find live/scheduled events that need API refresh — group by sport_type + date
        refresh_groups = {}  # key: (sport_type, date_str) -> list of events
        for ev in events:
            if ev.is_live or ev.status in ('live', 'scheduled'):
                date_str = ev.event_date.strftime('%Y-%m-%d') if ev.event_date else datetime.now().strftime('%Y-%m-%d')
                group_key = (ev.sport_type, date_str)
                refresh_groups.setdefault(group_key, []).append(ev)

        # 3. For each sport+date group, make ONE external API call and update matching events
        for (sport_type, date_str), group_events in refresh_groups.items():
            try:
                sport = SportsCategory.query.filter(
                    db.or_(SportsCategory.name == sport_type, SportsCategory.key == sport_type.lower())
                ).first()
                if not sport:
                    continue

                sport_key = sport.key
                endpoint = APISportsService._get_endpoint(sport_key)
                params = APISportsService._build_params(sport_key, 'all', date_str)

                import requests as req
                url = f"{sport.api_url}{endpoint}"
                response = req.get(
                    url,
                    headers=APISportsService._get_headers(sport.api_url),
                    params=params,
                    timeout=10
                )
                response.raise_for_status()
                data = response.json()
                resp_data = data.get('response', [])

                if resp_data:
                    api_events = APISportsService._transform_response(resp_data, sport.name, sport_key, sport.icon)
                    # Build lookup from external_id -> fresh data
                    api_lookup = {str(ae.get('id', '')): ae for ae in api_events}

                    # Match and update each event in this group
                    # (same fields as _import_sport for existing events)
                    for ev in group_events:
                        if ev.external_id and ev.external_id in api_lookup:
                            fresh = api_lookup[ev.external_id]
                            ev.name = fresh.get('name', ev.name)
                            ev.score_home = fresh.get('scoreHome', ev.score_home)
                            ev.score_away = fresh.get('scoreAway', ev.score_away)
                            ev.status = fresh.get('status', ev.status)
                            ev.is_live = fresh.get('isLive', ev.is_live)
                            ev.venue = fresh.get('venue', ev.venue)
                            ev.thumbnail_url = fresh.get('thumbnailUrl', ev.thumbnail_url)
                            ev.league = fresh.get('league', ev.league)
                            raw_date = fresh.get('eventDate')
                            if raw_date:
                                try:
                                    ev.event_date = datetime.fromisoformat(raw_date.replace('Z', '+00:00'))
                                except (ValueError, AttributeError):
                                    try:
                                        ev.event_date = datetime.strptime(raw_date[:19], '%Y-%m-%dT%H:%M:%S')
                                    except Exception:
                                        pass
                            ev.updated_at = datetime.utcnow()
            except Exception as e:
                print(f"[BatchRefresh] Error refreshing {sport_type}/{date_str}: {e}")

        # 4. Commit all updates at once
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()

        # 5. Return results in the originally-requested order
        results = []
        for eid in event_ids:
            ev = event_map.get(eid)
            if ev:
                results.append(ev.to_dict())

        return jsonify({
            'success': True,
            'count': len(results),
            'data': results
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@sports_bp.route('/categories', methods=['GET'])
@cache.cached(timeout=3600)
def get_categories():
    """Get active sports categories"""
    try:
        from models.media import SportsCategory
        categories = SportsCategory.query.filter_by(is_active=True).order_by(SportsCategory.name).all()
        return jsonify({
            'success': True,
            'count': len(categories),
            'data': [c.to_dict() for c in categories]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@sports_bp.route('/events/<int:event_id>/details', methods=['GET'])
@cache.cached(timeout=60, query_string=True)
def get_event_match_detail(event_id):
    """
    Proxy enriched match data from API-Sports.
    Returns events timeline, statistics, lineups, player stats.
    """
    try:
        from models.media import SportsEvent as SE
        from services.sports_detail_service import get_match_detail

        ev = SE.query.get(event_id)
        if not ev:
            return jsonify({'success': False, 'error': 'Event not found'}), 404

        ext = ev.external_id or ''
        parts = ext.split('-', 1)
        if len(parts) != 2:
            return jsonify({'success': True, 'data': {
                'events': [], 'statistics': [], 'lineups': [], 'periods': [], 'players': []
            }})

        sport_key, api_id = parts[0], parts[1]
        data = get_match_detail(sport_key, api_id)
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@sports_bp.route('/standings', methods=['GET'])
@cache.cached(timeout=3600, query_string=True)
def get_standings():
    """
    Get league standings.
    Query params: sport (key), league (API league ID), season (optional, defaults to current year)
    """
    try:
        from services.sports_detail_service import get_standings as fetch_standings

        sport_key = request.args.get('sport')
        league_id = request.args.get('league')
        season = request.args.get('season')

        if not sport_key or not league_id:
            return jsonify({'success': False, 'error': 'sport and league params required'}), 400

        data = fetch_standings(sport_key, int(league_id), int(season) if season else None)
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@sports_bp.route('/h2h', methods=['GET'])
@cache.cached(timeout=3600, query_string=True)
def get_head_to_head():
    """
    Get head-to-head past matches.
    Query params: sport (key), team1 (API team ID), team2 (API team ID)
    """
    try:
        from services.sports_detail_service import get_h2h

        sport_key = request.args.get('sport')
        team1 = request.args.get('team1')
        team2 = request.args.get('team2')

        if not sport_key or not team1 or not team2:
            return jsonify({'success': False, 'error': 'sport, team1, team2 params required'}), 400

        data = get_h2h(sport_key, team1, team2)
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@sports_bp.route('/predictions/<int:event_id>', methods=['GET'])
@cache.cached(timeout=3600, query_string=True)
def get_match_predictions(event_id):
    """
    Get AI predictions for a match (Football only on free tier).
    """
    try:
        from models.media import SportsEvent as SE
        from services.sports_detail_service import get_predictions

        ev = SE.query.get(event_id)
        if not ev:
            return jsonify({'success': False, 'error': 'Event not found'}), 404

        ext = ev.external_id or ''
        parts = ext.split('-', 1)
        if len(parts) != 2:
            return jsonify({'success': True, 'data': None})

        sport_key, api_id = parts[0], parts[1]
        data = get_predictions(sport_key, api_id)
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@sports_bp.route('/leagues', methods=['GET'])
@cache.cached(timeout=60, query_string=True)
def get_leagues():
    """Get unique leagues from stored events"""
    try:
        from models.media import SportsEvent, db
        from sqlalchemy import func

        date = request.args.get('date')
        sport = request.args.get('sport')

        query = db.session.query(
            SportsEvent.league
        ).filter(SportsEvent.league.isnot(None))

        if date:
            try:
                d = datetime.strptime(date, '%Y-%m-%d')
                query = query.filter(db.func.date(SportsEvent.event_date) == d.date())
            except ValueError:
                pass

        if sport and sport != 'All':
            query = query.filter(SportsEvent.sport_type == sport)

        leagues = query.distinct().all()
        league_names = sorted([l[0] for l in leagues if l[0]])

        return jsonify({
            'success': True,
            'data': [{'name': name} for name in league_names]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
