"""
Public Media Routes - TV Channels and Radio Stations
No auth required, country-filtered based on X-User-Country header
"""
from flask import Blueprint, jsonify, request
from models import db, TVChannel, RadioStation

media_bp = Blueprint('media', __name__, url_prefix='/api/media')


def get_user_country():
    """Get country from X-User-Country header"""
    hc = request.headers.get('X-User-Country')
    if hc is None:
        return None
    return hc.strip().upper() or None


def apply_country_filter(query, model, country_code_field='country_code'):
    """Apply country filter if header is present"""
    header_country = get_user_country()
    
    # support models that use either 'country_code' or 'country'
    column = getattr(model, country_code_field, None) or getattr(model, 'country', None)
    if column is None:
        return query

    if header_country:
        # If header present, return [country, 'GLOBAL']
        # Note: 'country' field might use full names like 'United States'
        if country_code_field == 'country_code':
            return query.filter(column.in_([header_country, 'GLOBAL']))
        else:
            # for 'country' field, we might need mapping, but for now just use header
            return query.filter(column == header_country)
    else:
        # If no header, return ONLY 'GLOBAL'
        return query.filter(column == 'GLOBAL')


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

        # enforce country scoping for single item
        header_country = request.headers.get('X-User-Country')
        channel_country = (channel.country_code or '').upper()
        if header_country:
            hc = header_country.strip().upper()
            if channel_country not in [hc, 'GLOBAL']:
                channel = None
        else:
            if channel_country != 'GLOBAL':
                channel = None
        
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

        # enforce country scoping for single item
        header_country = request.headers.get('X-User-Country')
        station_country = (getattr(station, 'country', None) or getattr(station, 'country_code', None) or '').upper()
        if header_country:
            hc = header_country.strip().upper()
            # Note: station_country might be 'UNITED STATES' while hc is 'US'
            # For now, we assume codes are used or names match
            if station_country not in [hc, 'GLOBAL']:
                # Simple check for US/United States
                if not (hc == 'US' and station_country == 'UNITED STATES'):
                    station = None
        else:
            if station_country != 'GLOBAL':
                station = None
        
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
            'sportType': e.sport_type,
            'league': e.league,
            'status': e.status,
            'venue': e.venue,
            'teamHome': e.team_home,
            'teamAway': e.team_away,
            'scoreHome': e.score_home,
            'scoreAway': e.score_away,
            'eventDate': e.event_date.isoformat() if e.event_date else None,
            'streamUrl': e.stream_url,
            'thumbnailUrl': e.thumbnail_url,
            'countryCode': e.country_code,
            'isLive': e.is_live
        } for e in events])
    except ImportError:
        # SportsEvent model doesn't exist yet, return empty list
        return jsonify([])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@media_bp.route('/sports-events/<id>', methods=['GET'])
def get_sports_event(id):
    """Get single sports event by ID with country scoping"""
    try:
        from models import SportsEvent

        event = SportsEvent.query.filter(SportsEvent.id == id, SportsEvent.is_active == True).first()
        if not event:
            return jsonify({'error': 'Event not found'}), 404

        # enforce country scoping for single item
        header_country = request.headers.get('X-User-Country')
        event_country = (getattr(event, 'country_code', None) or getattr(event, 'country', None) or '').upper()
        if header_country:
            hc = header_country.strip().upper()
            if event_country not in [hc, 'GLOBAL']:
                event = None
        else:
            if event_country != 'GLOBAL':
                event = None

        return jsonify({
            'id': str(event.id),
            'name': event.name,
            'sportType': event.sport_type,
            'league': event.league,
            'status': event.status,
            'venue': event.venue,
            'teamHome': event.team_home,
            'teamAway': event.team_away,
            'scoreHome': event.score_home,
            'scoreAway': event.score_away,
            'eventDate': event.event_date.isoformat() if event.event_date else None,
            'streamUrl': event.stream_url,
            'thumbnailUrl': event.thumbnail_url,
            'countryCode': event.country_code,
            'isLive': event.is_live
        })
    except ImportError:
        return jsonify({'error': 'SportsEvent model not available'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

