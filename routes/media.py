"""
Public Media Routes - TV Channels and Radio Stations
No auth required, country-filtered based on X-User-Country header
"""
from flask import Blueprint, jsonify, request
from models import db, TVChannel, RadioStation

media_bp = Blueprint('media', __name__, url_prefix='/api/media')


def get_user_country():
    """Get country from X-User-Country header"""
    return request.headers.get('X-User-Country', '').strip().upper() or None


def apply_country_filter(query, model, country_code_field='country_code'):
    """Apply country filter if header is present"""
    country = get_user_country()
    if country:
        column = getattr(model, country_code_field, None)
        if column is not None:
            return query.filter(column == country)
    return query


# ============================================================================
# TV CHANNELS (Public)
# ============================================================================

@media_bp.route('/tv-channels', methods=['GET'])
def get_tv_channels():
    """List TV channels (public, country-filtered)"""
    try:
        query = TVChannel.query.filter(TVChannel.is_active == True)
        query = apply_country_filter(query, TVChannel)
        query = query.order_by(TVChannel.sort_order, TVChannel.name)
        
        channels = query.all()
        return jsonify([{
            'id': c.id,
            'name': c.name,
            'category': c.category,
            'logo_url': c.logo_url,
            'stream_url': c.stream_url,
            'country_code': c.country_code,
            'language': c.language,
            'description': c.description,
            'is_live': c.is_live,
            'is_premium': c.is_premium
        } for c in channels])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@media_bp.route('/tv-channels/<id>', methods=['GET'])
def get_tv_channel(id):
    """Get single TV channel by ID"""
    try:
        channel = TVChannel.query.filter(TVChannel.id == id, TVChannel.is_active == True).first()
        if not channel:
            return jsonify({'error': 'Channel not found'}), 404
        
        return jsonify({
            'id': channel.id,
            'name': channel.name,
            'category': channel.category,
            'logo_url': channel.logo_url,
            'stream_url': channel.stream_url,
            'country_code': channel.country_code,
            'language': channel.language,
            'description': channel.description,
            'is_live': channel.is_live,
            'is_premium': channel.is_premium
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# RADIO STATIONS (Public)
# ============================================================================

@media_bp.route('/radio-stations', methods=['GET'])
def get_radio_stations():
    """List radio stations (public, country-filtered)"""
    try:
        query = RadioStation.query.filter(RadioStation.is_active == True)
        query = apply_country_filter(query, RadioStation)
        query = query.order_by(RadioStation.position, RadioStation.name)
        
        stations = query.all()
        return jsonify([{
            'id': s.id,
            'name': s.name,
            'stream_url': s.stream_url,
            'website_url': s.website_url,
            'logo_url': s.logo_url,
            'country': s.country,
            'genre': s.genre,
            'language': s.language,
            'bitrate': s.bitrate,
            'description': s.description
        } for s in stations])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@media_bp.route('/radio-stations/<int:id>', methods=['GET'])
def get_radio_station(id):
    """Get single radio station by ID"""
    try:
        station = RadioStation.query.filter(RadioStation.id == id, RadioStation.is_active == True).first()
        if not station:
            return jsonify({'error': 'Station not found'}), 404
        
        return jsonify({
            'id': station.id,
            'name': station.name,
            'stream_url': station.stream_url,
            'website_url': station.website_url,
            'logo_url': station.logo_url,
            'country': station.country,
            'genre': station.genre,
            'language': station.language,
            'bitrate': station.bitrate,
            'description': station.description
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# SPORTS EVENTS (Public)
# ============================================================================

@media_bp.route('/sports-events', methods=['GET'])
def get_sports_events():
    """List sports events (public, country-filtered)"""
    try:
        # Check if SportsEvent model exists
        from models import SportsEvent
        
        query = SportsEvent.query.filter(SportsEvent.is_active == True)
        query = apply_country_filter(query, SportsEvent)
        query = query.order_by(SportsEvent.event_date.desc())
        
        events = query.all()
        return jsonify([{
            'id': str(e.id),
            'name': e.name,
            'description': e.description,
            'category': e.category,
            'status': e.status,
            'logo': e.logo_url,
            'embed_url': e.embed_url,
            'venue': e.venue,
            'match_type': e.match_type,
            'team_home': e.team_home,
            'team_away': e.team_away,
            'score_home': e.score_home,
            'score_away': e.score_away,
            'event_date': e.event_date.isoformat() if e.event_date else None,
            'result': e.result,
            'series': e.series
        } for e in events])
    except ImportError:
        # SportsEvent model doesn't exist yet, return empty list
        return jsonify([])
    except Exception as e:
        return jsonify({'error': str(e)}), 500
