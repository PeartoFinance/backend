"""
Admin Media Routes - TV Channels and Radio Stations
With country-specific filtering
"""
from flask import Blueprint, jsonify, request
from ..decorators import admin_required
from models import db, TVChannel, RadioStation
import uuid
from datetime import datetime

media_bp = Blueprint('admin_media', __name__)


# ============================================================================
# TV CHANNELS
# ============================================================================

@media_bp.route('/media/tv-channels', methods=['GET'])
@admin_required
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
@admin_required
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
@admin_required
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
@admin_required
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
@admin_required
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
@admin_required
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
@admin_required
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
@admin_required
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
@admin_required
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
