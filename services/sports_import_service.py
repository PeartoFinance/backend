"""
Sports Import Service
Fetches events from the external API-Sports APIs and stores them in the DB.
Used by cron jobs and admin manual import.
"""
from datetime import datetime
from models.media import SportsEvent, SportsCategory, db
from services.api_sports_service import APISportsService


class SportsImportService:
    """Import sports events from API-Sports into the local database."""

    @staticmethod
    def import_events(date=None, sport_key=None):
        """
        Fetch events from external API and upsert into sports_events table.
        :param date: YYYY-MM-DD string (defaults to today)
        :param sport_key: optional — limit import to one sport (e.g. 'football')
        :returns: dict with import stats
        """
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')

        stats = {'imported': 0, 'updated': 0, 'errors': 0, 'sport_details': {}}

        try:
            # Get active sports (or a specific one)
            if sport_key:
                active_sports = SportsCategory.query.filter_by(key=sport_key, is_active=True).all()
            else:
                active_sports = SportsCategory.query.filter_by(is_active=True).all()

            if not active_sports:
                return {**stats, 'message': 'No active sports found'}

            for sport in active_sports:
                try:
                    sport_stats = SportsImportService._import_sport(sport, date)
                    stats['imported'] += sport_stats['imported']
                    stats['updated'] += sport_stats['updated']
                    stats['errors'] += sport_stats['errors']
                    stats['sport_details'][sport.name] = sport_stats
                except Exception as e:
                    print(f"[SportsImport] Error importing {sport.name}: {e}")
                    stats['errors'] += 1
                    stats['sport_details'][sport.name] = {'error': str(e)}

            db.session.commit()
            stats['message'] = f"Import complete: {stats['imported']} new, {stats['updated']} updated"
        except Exception as e:
            db.session.rollback()
            stats['message'] = f"Import failed: {str(e)}"
            stats['errors'] += 1

        return stats

    @staticmethod
    def _import_sport(sport, date):
        """Import events for a single sport."""
        sport_key = sport.key
        endpoint = APISportsService._get_endpoint(sport_key)
        params = APISportsService._build_params(sport_key, 'all', date)

        stats = {'imported': 0, 'updated': 0, 'errors': 0, 'total_api': 0}

        import requests as req
        url = f"{sport.api_url}{endpoint}"
        print(f"[SportsImport] Fetching {sport.name} from {url} params={params}")

        response = req.get(
            url,
            headers=APISportsService._get_headers(sport.api_url),
            params=params,
            timeout=15
        )
        response.raise_for_status()
        data = response.json()

        if data.get('errors') and len(data['errors']) > 0:
            err_msg = str(data['errors'])
            print(f"[SportsImport] API errors for {sport.name}: {err_msg}")
            # If plan restriction, still continue — just means 0 events
            if 'plan' in err_msg.lower():
                stats['errors'] = 0
                return stats

        resp_data = data.get('response', [])
        if not resp_data:
            print(f"[SportsImport] No events for {sport.name}")
            return stats

        # Transform to our normalized format
        events = APISportsService._transform_response(resp_data, sport.name, sport_key, sport.icon)
        stats['total_api'] = len(events)
        print(f"[SportsImport] Got {len(events)} events for {sport.name}")

        # Upsert each event — use no_autoflush block to avoid cascading errors
        for event_data in events:
            try:
                external_id = str(event_data.get('id', ''))
                if not external_id:
                    stats['errors'] += 1
                    continue

                with db.session.no_autoflush:
                    existing = SportsEvent.query.filter_by(external_id=external_id).first()

                # Parse event date
                event_date = None
                raw_date = event_data.get('eventDate')
                if raw_date:
                    try:
                        event_date = datetime.fromisoformat(raw_date.replace('Z', '+00:00'))
                    except (ValueError, AttributeError):
                        try:
                            event_date = datetime.strptime(raw_date[:19], '%Y-%m-%dT%H:%M:%S')
                        except Exception:
                            event_date = None

                # Truncate country_code to be safe
                country_code = event_data.get('countryCode')
                if country_code and len(str(country_code)) > 100:
                    country_code = str(country_code)[:100]

                if existing:
                    # Update existing event
                    existing.name = event_data.get('name', existing.name)
                    existing.score_home = event_data.get('scoreHome', existing.score_home)
                    existing.score_away = event_data.get('scoreAway', existing.score_away)
                    existing.status = event_data.get('status', existing.status)
                    existing.is_live = event_data.get('isLive', existing.is_live)
                    existing.venue = event_data.get('venue', existing.venue)
                    existing.thumbnail_url = event_data.get('thumbnailUrl', existing.thumbnail_url)
                    existing.league = event_data.get('league', existing.league)
                    if event_date:
                        existing.event_date = event_date
                    existing.updated_at = datetime.utcnow()
                    stats['updated'] += 1
                else:
                    # Create new event
                    new_event = SportsEvent(
                        external_id=external_id,
                        name=event_data.get('name', 'Unknown'),
                        sport_type=event_data.get('sportType'),
                        league=event_data.get('league'),
                        team_home=event_data.get('teamHome'),
                        team_away=event_data.get('teamAway'),
                        score_home=event_data.get('scoreHome'),
                        score_away=event_data.get('scoreAway'),
                        event_date=event_date,
                        venue=event_data.get('venue'),
                        status=event_data.get('status', 'scheduled'),
                        stream_url=event_data.get('streamUrl'),
                        thumbnail_url=event_data.get('thumbnailUrl'),
                        country_code=country_code,
                        is_active=event_data.get('isActive', True),
                        is_live=event_data.get('isLive', False),
                    )
                    db.session.add(new_event)
                    stats['imported'] += 1

            except Exception as e:
                print(f"[SportsImport] Error upserting event {event_data.get('id')}: {e}")
                db.session.rollback()
                stats['errors'] += 1
                continue

        # Flush to catch any DB errors early
        try:
            db.session.flush()
        except Exception as e:
            print(f"[SportsImport] Flush error for {sport.name}: {e}")
            db.session.rollback()
            stats['errors'] += 1

        return stats

    @staticmethod
    def refresh_live_events():
        """
        Refresh only LIVE events — used for real-time score updates.
        Fetches live data from API and updates existing DB records.
        """
        stats = {'updated': 0, 'errors': 0}

        try:
            active_sports = SportsCategory.query.filter_by(is_active=True).all()

            for sport in active_sports:
                try:
                    sport_key = sport.key
                    endpoint = APISportsService._get_endpoint(sport_key)
                    params = {'live': 'all'}

                    import requests as req
                    url = f"{sport.api_url}{endpoint}"
                    response = req.get(
                        url,
                        headers=APISportsService._get_headers(sport.api_url),
                        params=params,
                        timeout=15
                    )
                    response.raise_for_status()
                    data = response.json()

                    resp_data = data.get('response', [])
                    if not resp_data:
                        continue

                    events = APISportsService._transform_response(resp_data, sport.name, sport_key, sport.icon)

                    for event_data in events:
                        external_id = str(event_data.get('id', ''))
                        if not external_id:
                            continue

                        existing = SportsEvent.query.filter_by(external_id=external_id).first()
                        if existing:
                            # Same fields as _import_sport, batch-refresh, and single-event refresh
                            existing.name = event_data.get('name', existing.name)
                            existing.score_home = event_data.get('scoreHome', existing.score_home)
                            existing.score_away = event_data.get('scoreAway', existing.score_away)
                            existing.status = event_data.get('status', existing.status)
                            existing.is_live = event_data.get('isLive', existing.is_live)
                            existing.venue = event_data.get('venue', existing.venue)
                            existing.thumbnail_url = event_data.get('thumbnailUrl', existing.thumbnail_url)
                            existing.league = event_data.get('league', existing.league)
                            raw_date = event_data.get('eventDate')
                            if raw_date:
                                try:
                                    existing.event_date = datetime.fromisoformat(raw_date.replace('Z', '+00:00'))
                                except (ValueError, AttributeError):
                                    try:
                                        existing.event_date = datetime.strptime(raw_date[:19], '%Y-%m-%dT%H:%M:%S')
                                    except Exception:
                                        pass
                            existing.updated_at = datetime.utcnow()
                            stats['updated'] += 1

                except Exception as e:
                    print(f"[SportsImport] Error refreshing live {sport.name}: {e}")
                    stats['errors'] += 1
                    continue

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            stats['errors'] += 1
            print(f"[SportsImport] Live refresh failed: {e}")

        return stats

    @staticmethod
    def get_single_event_fresh(event_id):
        """
        Fetch a single event from DB. If it's live, try to refresh from API first.
        :param event_id: DB primary key id
        """
        event = SportsEvent.query.get(event_id)
        if not event:
            return None

        # If event is live or scheduled, try to get fresh data
        if event.is_live or event.status in ('live', 'scheduled'):
            try:
                external_id = event.external_id or ''
                # Parse sport key and API id from external_id like "football-12345"
                parts = external_id.rsplit('-', 1)
                if len(parts) == 2:
                    sport_prefix = parts[0]
                    # Find matching category
                    sport = SportsCategory.query.filter(
                        SportsCategory.key == sport_prefix
                    ).first()

                    if not sport:
                        # Try matching by sport_type
                        sport = SportsCategory.query.filter(
                            SportsCategory.name == event.sport_type
                        ).first()

                    if sport:
                        sport_key = sport.key
                        endpoint = APISportsService._get_endpoint(sport_key)
                        # Fetch by date to find the specific event
                        date_str = event.event_date.strftime('%Y-%m-%d') if event.event_date else datetime.now().strftime('%Y-%m-%d')
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
                            events = APISportsService._transform_response(resp_data, sport.name, sport_key, sport.icon)
                            # Find the matching event
                            for ev in events:
                                if str(ev.get('id', '')) == external_id:
                                    # Update same fields as _import_sport & batch-refresh
                                    event.name = ev.get('name', event.name)
                                    event.score_home = ev.get('scoreHome', event.score_home)
                                    event.score_away = ev.get('scoreAway', event.score_away)
                                    event.status = ev.get('status', event.status)
                                    event.is_live = ev.get('isLive', event.is_live)
                                    event.venue = ev.get('venue', event.venue)
                                    event.thumbnail_url = ev.get('thumbnailUrl', event.thumbnail_url)
                                    event.league = ev.get('league', event.league)
                                    raw_date = ev.get('eventDate')
                                    if raw_date:
                                        try:
                                            event.event_date = datetime.fromisoformat(raw_date.replace('Z', '+00:00'))
                                        except (ValueError, AttributeError):
                                            try:
                                                event.event_date = datetime.strptime(raw_date[:19], '%Y-%m-%dT%H:%M:%S')
                                            except Exception:
                                                pass
                                    event.updated_at = datetime.utcnow()
                                    db.session.commit()
                                    break

            except Exception as e:
                print(f"[SportsImport] Error refreshing single event {event_id}: {e}")

        return event
