"""
Admin Media Routes - TV Channels and Radio Stations
With country-specific filtering
"""
from flask import Blueprint, jsonify, request
from ..decorators import admin_required, permission_required
from models import db, TVChannel, RadioStation
import uuid
from datetime import datetime

media_bp = Blueprint('admin_media', __name__)


# ============================================================================
# TV CHANNELS
# ============================================================================

@media_bp.route('/media/tv-channels', methods=['GET'])
@permission_required("tv_manage")
def get_tv_channels():
    """List all TV channels (country-filtered)"""
    try:
        country = getattr(request, 'user_country', 'US')
        channels = TVChannel.query.filter(
            (TVChannel.country_code == country) | 
            (TVChannel.country_code == 'GLOBAL')
        ).order_by(TVChannel.sort_order, TVChannel.name).all()
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
            'is_premium': c.is_premium,
            'is_active': c.is_active,
            'sort_order': c.sort_order
        } for c in channels])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@media_bp.route('/media/tv-channels', methods=['POST'])
@permission_required("tv_manage")
def create_tv_channel():
    """Create a TV channel"""
    try:
        data = request.get_json()
        channel = TVChannel(
            id=str(uuid.uuid4()),
            name=data['name'],
            category=data.get('category'),
            logo_url=data.get('logo_url'),
            stream_url=data.get('stream_url'),
            country_code=data.get('country_code', getattr(request, 'user_country', 'US')),
            language=data.get('language'),
            description=data.get('description'),
            is_live=data.get('is_live', False),
            is_premium=data.get('is_premium', False),
            is_active=data.get('is_active', True),
            sort_order=data.get('sort_order', 0)
        )
        db.session.add(channel)
        db.session.commit()
        return jsonify({'ok': True, 'id': channel.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@media_bp.route('/media/tv-channels/<id>', methods=['PUT', 'PATCH'])
@permission_required("tv_manage")
def update_tv_channel(id):
    """Update a TV channel"""
    try:
        channel = TVChannel.query.get_or_404(id)
        data = request.get_json()
        for key in ['name', 'category', 'logo_url', 'stream_url', 'country_code', 'language', 
                    'description', 'is_live', 'is_premium', 'is_active', 'sort_order']:
            if key in data:
                setattr(channel, key, data[key])
        db.session.commit()
        return jsonify({'ok': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@media_bp.route('/media/tv-channels/<id>', methods=['DELETE'])
@permission_required("tv_manage")
def delete_tv_channel(id):
    """Delete a TV channel"""
    try:
        channel = TVChannel.query.get_or_404(id)
        db.session.delete(channel)
        db.session.commit()
        return jsonify({'ok': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============================================================================
# RADIO STATIONS
# ============================================================================

@media_bp.route('/media/radio-stations', methods=['GET'])
@permission_required("radio_manage")
def get_radio_stations():
    """List all radio stations (country-filtered)"""
    try:
        country = getattr(request, 'user_country', 'US')
        stations = RadioStation.query.filter(
            (RadioStation.country_code == country) | 
            (RadioStation.country_code == 'GLOBAL')
        ).order_by(RadioStation.position, RadioStation.name).all()
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
            'description': s.description,
            'is_active': s.is_active,
            'listeners_count': s.listeners_count,
            'country_code': s.country_code
        } for s in stations])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@media_bp.route('/media/radio-stations', methods=['POST'])
@permission_required("radio_manage")
def create_radio_station():
    """Create a radio station"""
    try:
        data = request.get_json()
        station = RadioStation(
            name=data['name'],
            stream_url=data['stream_url'],
            website_url=data.get('website_url'),
            logo_url=data.get('logo_url'),
            country=data.get('country'),
            genre=data.get('genre'),
            language=data.get('language'),
            bitrate=data.get('bitrate'),
            description=data.get('description'),
            is_active=data.get('is_active', True),
            country_code=data.get('country_code', getattr(request, 'user_country', 'US'))
        )
        db.session.add(station)
        db.session.commit()
        return jsonify({'ok': True, 'id': station.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@media_bp.route('/media/radio-stations/<int:id>', methods=['PUT', 'PATCH'])
@permission_required("radio_manage")
def update_radio_station(id):
    """Update a radio station"""
    try:
        station = RadioStation.query.get_or_404(id)
        data = request.get_json()
        for key in ['name', 'stream_url', 'website_url', 'logo_url', 'country', 
                    'genre', 'language', 'bitrate', 'description', 'is_active']:
            if key in data:
                setattr(station, key, data[key])
        db.session.commit()
        return jsonify({'ok': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@media_bp.route('/media/radio-stations/<int:id>', methods=['DELETE'])
@permission_required("radio_manage")
def delete_radio_station(id):
    """Delete a radio station"""
    try:
        station = RadioStation.query.get_or_404(id)
        db.session.delete(station)
        db.session.commit()
        return jsonify({'ok': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@media_bp.route('/media/radio-stations/import', methods=['POST'])
@permission_required("radio_manage")
def import_radio_stations():
    """Bulk import radio stations"""
    try:
        data = request.get_json()
        stations = data.get('stations', [])
        country_code = getattr(request, 'user_country', 'US')
        imported = 0
        
        for s in stations:
            if not s.get('name') or not s.get('stream_url'):
                continue
            station = RadioStation(
                name=s['name'],
                stream_url=s['stream_url'],
                website_url=s.get('website_url'),
                logo_url=s.get('logo_url'),
                country=s.get('country'),
                genre=s.get('genre'),
                language=s.get('language'),
                bitrate=s.get('bitrate'),
                is_active=True,
                country_code=country_code
            )
            db.session.add(station)
            imported += 1
        
        db.session.commit()
        return jsonify({'ok': True, 'imported': imported})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============================================================================
# SPORTS EVENTS
# ============================================================================

@media_bp.route('/media/sports-events', methods=['GET'])
@permission_required("live_sports")
def get_sports_events():
    """List all sports events (country-filtered)"""
    try:
        from models import SportsEvent
        country = getattr(request, 'user_country', 'US')
        
        events = SportsEvent.query.filter(
            (SportsEvent.country_code == country) | 
            (SportsEvent.country_code == 'GLOBAL')
        ).order_by(SportsEvent.event_date.desc()).all()
        
        return jsonify([{
            'id': e.id,
            'name': e.name,
            'sportType': e.sport_type,
            'league': e.league,
            'venue': e.venue,
            'teamHome': e.team_home,
            'teamAway': e.team_away,
            'scoreHome': e.score_home,
            'scoreAway': e.score_away,
            'eventDate': e.event_date.isoformat() if e.event_date else None,
            'status': e.status,
            'streamUrl': e.stream_url,
            'thumbnailUrl': e.thumbnail_url,
            'countryCode': e.country_code,
            'isLive': e.is_live,
            'isActive': e.is_active
        } for e in events])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@media_bp.route('/media/sports-events', methods=['POST'])
@permission_required("live_sports")
def create_sports_event():
    """Create a sports event"""
    try:
        from models import SportsEvent
        data = request.get_json()
        
        # Parse date if provided
        event_date = None
        if data.get('eventDate'):
            try:
                event_date = datetime.fromisoformat(data['eventDate'].replace('Z', '+00:00'))
            except:
                pass

        event = SportsEvent(
            name=data['name'],
            sport_type=data.get('sportType'),
            league=data.get('league'),
            venue=data.get('venue'),
            team_home=data.get('teamHome'),
            team_away=data.get('teamAway'),
            score_home=data.get('scoreHome'),
            score_away=data.get('scoreAway'),
            event_date=event_date,
            status=data.get('status', 'scheduled'),
            stream_url=data.get('streamUrl'),
            thumbnail_url=data.get('thumbnailUrl'),
            country_code=data.get('countryCode', getattr(request, 'user_country', 'US')),
            is_live=data.get('isLive', False),
            is_active=data.get('isActive', True)
        )
        db.session.add(event)
        db.session.commit()
        return jsonify({'ok': True, 'id': event.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@media_bp.route('/media/sports-events/<int:id>', methods=['PUT', 'PATCH'])
@permission_required("live_sports")
def update_sports_event(id):
    """Update a sports event"""
    try:
        from models import SportsEvent
        event = SportsEvent.query.get_or_404(id)
        data = request.get_json()
        
        # Mapping frontend camelCase to model snake_case
        field_map = {
            'name': 'name',
            'sportType': 'sport_type',
            'league': 'league',
            'venue': 'venue',
            'teamHome': 'team_home',
            'teamAway': 'team_away',
            'scoreHome': 'score_home',
            'scoreAway': 'score_away',
            'status': 'status',
            'streamUrl': 'stream_url',
            'thumbnailUrl': 'thumbnail_url',
            'countryCode': 'country_code',
            'isLive': 'is_live',
            'isActive': 'is_active'
        }
        
        for key, model_field in field_map.items():
            if key in data:
                setattr(event, model_field, data[key])
                
        if 'eventDate' in data:
            try:
                event.event_date = datetime.fromisoformat(data['eventDate'].replace('Z', '+00:00')) if data['eventDate'] else None
            except:
                pass

        db.session.commit()
        return jsonify({'ok': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@media_bp.route('/media/sports-events/<int:id>', methods=['DELETE'])
@permission_required("live_sports")
def delete_sports_event(id):
    """Delete a sports event"""
    try:
        from models import SportsEvent
        event = SportsEvent.query.get_or_404(id)
        db.session.delete(event)
        db.session.commit()
        return jsonify({'ok': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
