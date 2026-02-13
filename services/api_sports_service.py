
import requests
import os
from datetime import datetime, timedelta
from extensions import cache
from config import config

class APISportsService:
    """
    Service to interact with API-Sports (multi-sport)
    Supports: Football, Basketball, Baseball, NBA, NFL, Rugby, Hockey, AFL,
    Handball, Volleyball, Formula 1, MMA
    """
    
    API_KEY = os.getenv('API_SPORTS_KEY')

    # Map sport key -> correct API endpoint path
    # Football (v3) uses /fixtures; all other sports use /games
    SPORT_ENDPOINTS = {
        'football': '/fixtures',
        'basketball': '/games',
        'baseball': '/games',
        'nba': '/games',
        'nfl': '/games',
        'rugby': '/games',
        'hockey': '/games',
        'afl': '/games',
        'handball': '/games',
        'volleyball': '/games',
        'formula-1': '/races',
        'mma': '/fights',
    }

    # Sports that use "game" wrapper in response (instead of "fixture")
    GAME_WRAPPER_SPORTS = {'nfl'}

    # Sports that return flat response (no fixture/game wrapper)
    FLAT_RESPONSE_SPORTS = {'basketball', 'baseball', 'nba', 'rugby', 'hockey',
                            'afl', 'handball', 'volleyball'}

    @classmethod
    def _get_headers(cls, api_url):
        if not cls.API_KEY:
            print("WARNING: API_SPORTS_KEY not found in environment variables")
        
        host = api_url.replace('https://', '').split('/')[0]
            
        return {
            'x-rapidapi-host': host,
            'x-rapidapi-key': cls.API_KEY
        }

    @classmethod
    def _get_endpoint(cls, sport_key):
        """Get the correct API endpoint for a sport"""
        return cls.SPORT_ENDPOINTS.get(sport_key, '/games')

    @classmethod
    def _build_params(cls, sport_key, status, date):
        """Build sport-specific query parameters.
        NOTE: We do NOT send 'season' params because the Free plan only allows
        seasons 2022-2024. Using just 'date' works for all sports on the free plan.
        """
        params = {}

        if status == 'live':
            params['live'] = 'all'
        else:
            if not date:
                date = datetime.now().strftime('%Y-%m-%d')
            params['date'] = date

        return params

    @classmethod
    @cache.memoize(timeout=300)  # Cache for 5 minutes
    def get_fixtures(cls, status='live', date=None):
        """
        Get fixtures (matches) for all active sports
        :param status: 'live', 'upcoming', 'all'
        :param date: YYYY-MM-DD (optional, defaults to today for upcoming/all)
        """
        if not cls.API_KEY:
            return []

        from models.media import SportsCategory
        
        try:
            active_sports = SportsCategory.query.filter_by(is_active=True).all()
        except Exception as e:
            print(f"Error fetching sports categories: {e}")
            return []
            
        if not active_sports:
            print("No active sports found")
            return []

        all_events = []
        
        for sport in active_sports:
            sport_key = sport.key  # e.g. 'football', 'nba', 'nfl'
            endpoint = cls._get_endpoint(sport_key)
            params = cls._build_params(sport_key, status, date)

            try:
                url = f"{sport.api_url}{endpoint}"
                print(f"[Sports] Fetching {sport.name} from {url} params={params}")
                response = requests.get(
                    url,
                    headers=cls._get_headers(sport.api_url),
                    params=params,
                    timeout=15
                )
                response.raise_for_status()
                data = response.json()

                # Log errors from the API itself
                if data.get('errors') and len(data['errors']) > 0:
                    print(f"[Sports] API errors for {sport.name}: {data['errors']}")

                resp_data = data.get('response', [])
                if resp_data:
                    events = cls._transform_response(resp_data, sport.name, sport_key, sport.icon)
                    all_events.extend(events)
                    print(f"[Sports] Got {len(events)} events for {sport.name}")
                else:
                    print(f"[Sports] No events for {sport.name} (results={data.get('results', 0)})")
                    
            except requests.exceptions.HTTPError as e:
                print(f"[Sports] HTTP error for {sport.name}: {e} - {e.response.text if e.response else ''}")
                continue
            except Exception as e:
                print(f"[Sports] Error fetching {sport.name}: {e}")
                continue
                
        return all_events

    @classmethod
    def _transform_response(cls, response_data, sport_name, sport_key, sport_icon=None):
        """Route to the correct transformer based on sport type"""
        if sport_key == 'football':
            return cls._transform_football(response_data, sport_name)
        elif sport_key in ('nfl',):
            return cls._transform_american_football(response_data, sport_name)
        elif sport_key == 'nba':
            return cls._transform_nba(response_data, sport_name)
        elif sport_key == 'basketball':
            return cls._transform_basketball(response_data, sport_name)
        elif sport_key == 'baseball':
            return cls._transform_baseball(response_data, sport_name)
        elif sport_key in ('rugby', 'hockey', 'afl', 'handball', 'volleyball'):
            return cls._transform_generic_game(response_data, sport_name)
        elif sport_key == 'formula-1':
            return cls._transform_formula1(response_data, sport_name)
        elif sport_key == 'mma':
            return cls._transform_mma(response_data, sport_name)
        else:
            # Fallback: try generic parser
            return cls._transform_generic_game(response_data, sport_name)

    # ============================
    # FOOTBALL (v3) - /fixtures
    # Response: { fixture: {id, date, venue, status}, league: {}, teams: {home, away}, goals: {home, away} }
    # ============================
    @staticmethod
    def _transform_football(fixtures_data, sport_name):
        events = []
        for item in fixtures_data:
            try:
                fixture = item.get('fixture', {})
                teams = item.get('teams', {})
                goals = item.get('goals', {})
                league = item.get('league', {})
                home = teams.get('home', {})
                away = teams.get('away', {})
                status_short = fixture.get('status', {}).get('short', '')

                score_home = str(goals.get('home')) if goals.get('home') is not None else '-'
                score_away = str(goals.get('away')) if goals.get('away') is not None else '-'

                events.append({
                    'id': f"football-{fixture.get('id', 0)}",
                    'name': f"{home.get('name', 'Unknown')} vs {away.get('name', 'Unknown')}",
                    'sportType': sport_name,
                    'league': league.get('name', 'Unknown League'),
                    'teamHome': home.get('name', 'Unknown'),
                    'teamAway': away.get('name', 'Unknown'),
                    'scoreHome': score_home,
                    'scoreAway': score_away,
                    'eventDate': fixture.get('date'),
                    'venue': fixture.get('venue', {}).get('name', 'Unknown Venue') if fixture.get('venue') else 'Unknown Venue',
                    'status': APISportsService._map_status(status_short),
                    'streamUrl': '',
                    'thumbnailUrl': league.get('logo'),
                    'countryCode': league.get('country'),
                    'isLive': status_short in ['1H', '2H', 'HT', 'ET', 'P', 'LIVE', 'BT'],
                    'isActive': True
                })
            except Exception as e:
                print(f"[Sports] Error parsing football fixture: {e}")
                continue
        return events

    # ============================
    # BASKETBALL / NBA - /games
    # Response: { id, date, time, timestamp, league: {}, country: {}, teams: {home, away}, scores: {home: {q1..q4,ot,total}, away: {...}}, status: {short, long} }
    # ============================
    @staticmethod
    def _transform_basketball(games_data, sport_name):
        events = []
        for item in games_data:
            try:
                game_id = item.get('id', 0)
                teams = item.get('teams', {})
                scores = item.get('scores', {})
                league = item.get('league', {})
                country = item.get('country', {})
                status_obj = item.get('status', {})
                status_short = status_obj.get('short', '') if isinstance(status_obj, dict) else ''
                home = teams.get('home', {})
                away = teams.get('away', {})

                # Scores: can be {home: {quarter_1..total}} or {home: {total: X}}
                score_home = '-'
                score_away = '-'
                home_scores = scores.get('home', {})
                away_scores = scores.get('away', {})
                if isinstance(home_scores, dict):
                    score_home = str(home_scores.get('total')) if home_scores.get('total') is not None else '-'
                elif home_scores is not None:
                    score_home = str(home_scores)
                if isinstance(away_scores, dict):
                    score_away = str(away_scores.get('total')) if away_scores.get('total') is not None else '-'
                elif away_scores is not None:
                    score_away = str(away_scores)

                events.append({
                    'id': f"{sport_name.lower().replace(' ', '-')}-{game_id}",
                    'name': f"{home.get('name', 'Unknown')} vs {away.get('name', 'Unknown')}",
                    'sportType': sport_name,
                    'league': league.get('name', 'Unknown League') if isinstance(league, dict) else 'Unknown League',
                    'teamHome': home.get('name', 'Unknown'),
                    'teamAway': away.get('name', 'Unknown'),
                    'scoreHome': score_home,
                    'scoreAway': score_away,
                    'eventDate': item.get('date') or item.get('time'),
                    'venue': 'N/A',
                    'status': APISportsService._map_status(status_short),
                    'streamUrl': '',
                    'thumbnailUrl': league.get('logo') if isinstance(league, dict) else None,
                    'countryCode': country.get('code') if isinstance(country, dict) else (league.get('country') if isinstance(league, dict) else None),
                    'isLive': status_short in ['Q1', 'Q2', 'Q3', 'Q4', 'OT', 'BT', 'HT', 'LIVE'],
                    'isActive': True
                })
            except Exception as e:
                print(f"[Sports] Error parsing basketball game: {e}")
                continue
        return events

    # ============================
    # NBA (v2) - /games
    # Response: { id, league: "standard", season, date: {start, end, duration}, stage, status: {clock, halftime, short (int), long},
    #   arena: {name, city, state}, teams: {visitors, home}, scores: {visitors: {points, linescore}, home: {points, linescore}} }
    # NOTE: NBA v2 uses 'visitors' (not 'away'), 'points' (not 'total'), status.short is a NUMBER
    # ============================
    @staticmethod
    def _transform_nba(games_data, sport_name):
        # NBA v2 status.short mapping: 1=Not Started, 2=In Progress, 3=Finished
        events = []
        for item in games_data:
            try:
                game_id = item.get('id', 0)
                teams = item.get('teams', {})
                scores = item.get('scores', {})
                arena = item.get('arena', {})
                status_obj = item.get('status', {})
                date_obj = item.get('date', {})

                home = teams.get('home', {})
                visitors = teams.get('visitors', {})

                # status.short is an int in NBA v2: 1=NS, 2=Live, 3=FT
                status_short_raw = status_obj.get('short', 1) if isinstance(status_obj, dict) else 1
                status_long = status_obj.get('long', '') if isinstance(status_obj, dict) else ''
                halftime = status_obj.get('halftime', False) if isinstance(status_obj, dict) else False

                if status_short_raw == 2 or halftime:
                    mapped_status = 'live'
                    is_live = True
                elif status_short_raw == 3 or status_long == 'Finished':
                    mapped_status = 'completed'
                    is_live = False
                else:
                    mapped_status = 'scheduled'
                    is_live = False

                # Scores: {home: {points: 93, linescore: [...]}, visitors: {points: 110, ...}}
                home_scores = scores.get('home', {})
                visitor_scores = scores.get('visitors', {})
                score_home = str(home_scores.get('points')) if isinstance(home_scores, dict) and home_scores.get('points') is not None else '-'
                score_away = str(visitor_scores.get('points')) if isinstance(visitor_scores, dict) and visitor_scores.get('points') is not None else '-'

                # Date is an object: {start: "2026-02-13T00:30:00.000Z", end, duration}
                event_date = date_obj.get('start') if isinstance(date_obj, dict) else item.get('date')

                # Arena
                arena_name = 'N/A'
                if isinstance(arena, dict) and arena.get('name'):
                    arena_name = arena['name']
                    if arena.get('city'):
                        arena_name += f", {arena['city']}"

                events.append({
                    'id': f"nba-{game_id}",
                    'name': f"{home.get('name', 'Unknown')} vs {visitors.get('name', 'Unknown')}",
                    'sportType': sport_name,
                    'league': 'NBA',
                    'teamHome': home.get('name', 'Unknown'),
                    'teamAway': visitors.get('name', 'Unknown'),
                    'scoreHome': score_home,
                    'scoreAway': score_away,
                    'eventDate': event_date,
                    'venue': arena_name,
                    'status': mapped_status,
                    'streamUrl': '',
                    'thumbnailUrl': home.get('logo') or visitors.get('logo'),
                    'countryCode': 'US',
                    'isLive': is_live,
                    'isActive': True
                })
            except Exception as e:
                print(f"[Sports] Error parsing NBA game: {e}")
                continue
        return events

    # ============================
    # BASEBALL - /games
    # Response: { id, date, time, league: {}, country: {}, teams: {home, away}, scores: {home: {innings, total, ...}, away: {...}}, status: {short} }
    # ============================
    @staticmethod
    def _transform_baseball(games_data, sport_name):
        events = []
        for item in games_data:
            try:
                game_id = item.get('id', 0)
                teams = item.get('teams', {})
                scores = item.get('scores', {})
                league = item.get('league', {})
                country = item.get('country', {})
                status_obj = item.get('status', {})
                status_short = status_obj.get('short', '') if isinstance(status_obj, dict) else ''
                home = teams.get('home', {})
                away = teams.get('away', {})

                score_home = '-'
                score_away = '-'
                home_scores = scores.get('home', {})
                away_scores = scores.get('away', {})
                if isinstance(home_scores, dict):
                    # Baseball: usually has 'total' or 'hits' -> 'total'
                    total = home_scores.get('total')
                    score_home = str(total) if total is not None else '-'
                elif home_scores is not None:
                    score_home = str(home_scores)
                if isinstance(away_scores, dict):
                    total = away_scores.get('total')
                    score_away = str(total) if total is not None else '-'
                elif away_scores is not None:
                    score_away = str(away_scores)

                events.append({
                    'id': f"baseball-{game_id}",
                    'name': f"{home.get('name', 'Unknown')} vs {away.get('name', 'Unknown')}",
                    'sportType': sport_name,
                    'league': league.get('name', 'Unknown League') if isinstance(league, dict) else 'Unknown League',
                    'teamHome': home.get('name', 'Unknown'),
                    'teamAway': away.get('name', 'Unknown'),
                    'scoreHome': score_home,
                    'scoreAway': score_away,
                    'eventDate': item.get('date') or item.get('time'),
                    'venue': 'N/A',
                    'status': APISportsService._map_status(status_short),
                    'streamUrl': '',
                    'thumbnailUrl': league.get('logo') if isinstance(league, dict) else None,
                    'countryCode': country.get('code') if isinstance(country, dict) else None,
                    'isLive': status_short in ['IN', 'LIVE', 'I1', 'I2', 'I3', 'I4', 'I5', 'I6', 'I7', 'I8', 'I9'],
                    'isActive': True
                })
            except Exception as e:
                print(f"[Sports] Error parsing baseball game: {e}")
                continue
        return events

    # ============================
    # AMERICAN FOOTBALL / NFL - /games
    # Response: { game: {id, date, venue, status: {short}}, league: {}, teams: {home, away}, scores: {home: {q1..q4,ot,total}, away: {...}} }
    # ============================
    @staticmethod
    def _transform_american_football(games_data, sport_name):
        events = []
        for item in games_data:
            try:
                game = item.get('game', {})
                teams = item.get('teams', {})
                scores = item.get('scores', {})
                league = item.get('league', {})
                home = teams.get('home', {})
                away = teams.get('away', {})
                status_obj = game.get('status', {})
                status_short = status_obj.get('short', '') if isinstance(status_obj, dict) else ''

                score_home = '-'
                score_away = '-'
                home_scores = scores.get('home', {})
                away_scores = scores.get('away', {})
                if isinstance(home_scores, dict):
                    score_home = str(home_scores.get('total')) if home_scores.get('total') is not None else '-'
                elif home_scores is not None:
                    score_home = str(home_scores)
                if isinstance(away_scores, dict):
                    score_away = str(away_scores.get('total')) if away_scores.get('total') is not None else '-'
                elif away_scores is not None:
                    score_away = str(away_scores)

                venue_obj = game.get('venue', {})
                venue_name = venue_obj.get('name', 'Unknown Venue') if isinstance(venue_obj, dict) else 'Unknown Venue'

                events.append({
                    'id': f"nfl-{game.get('id', 0)}",
                    'name': f"{home.get('name', 'Unknown')} vs {away.get('name', 'Unknown')}",
                    'sportType': sport_name,
                    'league': league.get('name', 'Unknown League') if isinstance(league, dict) else 'Unknown League',
                    'teamHome': home.get('name', 'Unknown'),
                    'teamAway': away.get('name', 'Unknown'),
                    'scoreHome': score_home,
                    'scoreAway': score_away,
                    'eventDate': game.get('date', {}).get('date') if isinstance(game.get('date'), dict) else game.get('date'),
                    'venue': venue_name,
                    'status': APISportsService._map_status(status_short),
                    'streamUrl': '',
                    'thumbnailUrl': league.get('logo') if isinstance(league, dict) else None,
                    'countryCode': league.get('country') if isinstance(league, dict) else None,
                    'isLive': status_short in ['Q1', 'Q2', 'Q3', 'Q4', 'OT', 'HT', 'LIVE'],
                    'isActive': True
                })
            except Exception as e:
                print(f"[Sports] Error parsing NFL game: {e}")
                continue
        return events

    # ============================
    # GENERIC GAME SPORTS (Rugby, Hockey, AFL, Handball, Volleyball) - /games
    # Response varies but usually: { id, date, teams: {home, away}, scores: {home: {..total}, away: {..total}}, status: {short}, league: {} }
    # ============================
    @staticmethod
    def _transform_generic_game(games_data, sport_name):
        events = []
        for item in games_data:
            try:
                # Some sports may have 'game' wrapper, others flat
                game_wrapper = item.get('game', None)
                if game_wrapper and isinstance(game_wrapper, dict) and 'id' in game_wrapper:
                    game_id = game_wrapper.get('id', 0)
                    event_date = game_wrapper.get('date')
                    status_obj = game_wrapper.get('status', {})
                    venue_obj = game_wrapper.get('venue', {})
                else:
                    game_id = item.get('id', 0)
                    event_date = item.get('date') or item.get('time')
                    status_obj = item.get('status', {})
                    venue_obj = {}

                teams = item.get('teams', {})
                scores = item.get('scores', {})
                league = item.get('league', {})
                country = item.get('country', {})
                home = teams.get('home', {})
                away = teams.get('away', {})
                status_short = status_obj.get('short', '') if isinstance(status_obj, dict) else ''

                score_home = '-'
                score_away = '-'
                home_scores = scores.get('home', {})
                away_scores = scores.get('away', {})
                if isinstance(home_scores, dict):
                    score_home = str(home_scores.get('total')) if home_scores.get('total') is not None else '-'
                elif home_scores is not None:
                    score_home = str(home_scores)
                if isinstance(away_scores, dict):
                    score_away = str(away_scores.get('total')) if away_scores.get('total') is not None else '-'
                elif away_scores is not None:
                    score_away = str(away_scores)

                venue_name = venue_obj.get('name', 'N/A') if isinstance(venue_obj, dict) else 'N/A'

                events.append({
                    'id': f"{sport_name.lower().replace(' ', '-')}-{game_id}",
                    'name': f"{home.get('name', 'Unknown')} vs {away.get('name', 'Unknown')}",
                    'sportType': sport_name,
                    'league': league.get('name', 'Unknown League') if isinstance(league, dict) else 'Unknown League',
                    'teamHome': home.get('name', 'Unknown'),
                    'teamAway': away.get('name', 'Unknown'),
                    'scoreHome': score_home,
                    'scoreAway': score_away,
                    'eventDate': event_date,
                    'venue': venue_name,
                    'status': APISportsService._map_status(status_short),
                    'streamUrl': '',
                    'thumbnailUrl': league.get('logo') if isinstance(league, dict) else None,
                    'countryCode': country.get('code') if isinstance(country, dict) else (league.get('country') if isinstance(league, dict) else None),
                    'isLive': status_short in ['Q1', 'Q2', 'Q3', 'Q4', 'OT', 'HT', 'LIVE', '1H', '2H', 'IN', 'BT', 'S1', 'S2', 'S3', 'S4', 'S5'],
                    'isActive': True
                })
            except Exception as e:
                print(f"[Sports] Error parsing {sport_name} game: {e}")
                continue
        return events

    # ============================
    # FORMULA 1 - /races
    # ============================
    @staticmethod
    def _transform_formula1(races_data, sport_name):
        events = []
        for item in races_data:
            try:
                competition = item.get('competition', {})
                circuit = item.get('circuit', {})
                race_id = item.get('id', 0)
                status_val = item.get('status', '')

                events.append({
                    'id': f"f1-{race_id}",
                    'name': competition.get('name', 'Unknown Race'),
                    'sportType': sport_name,
                    'league': 'Formula 1',
                    'teamHome': competition.get('name', ''),
                    'teamAway': '',
                    'scoreHome': '-',
                    'scoreAway': '-',
                    'eventDate': item.get('date'),
                    'venue': circuit.get('name', 'Unknown Circuit') if isinstance(circuit, dict) else 'Unknown Circuit',
                    'status': 'live' if status_val == 'In Progress' else ('completed' if status_val == 'Completed' else 'scheduled'),
                    'streamUrl': '',
                    'thumbnailUrl': circuit.get('image') if isinstance(circuit, dict) else None,
                    'countryCode': competition.get('location', {}).get('country') if isinstance(competition.get('location'), dict) else None,
                    'isLive': status_val == 'In Progress',
                    'isActive': True
                })
            except Exception as e:
                print(f"[Sports] Error parsing F1 race: {e}")
                continue
        return events

    # ============================
    # MMA - /fights
    # ============================
    @staticmethod
    def _transform_mma(fights_data, sport_name):
        events = []
        for item in fights_data:
            try:
                fight_id = item.get('id', 0)
                fighters = item.get('fighters', {})
                first = fighters.get('first', {}) if isinstance(fighters, dict) else {}
                second = fighters.get('second', {}) if isinstance(fighters, dict) else {}
                league = item.get('league', {})
                status_val = item.get('status', '')

                events.append({
                    'id': f"mma-{fight_id}",
                    'name': f"{first.get('name', 'Fighter 1')} vs {second.get('name', 'Fighter 2')}",
                    'sportType': sport_name,
                    'league': league.get('name', 'Unknown') if isinstance(league, dict) else 'Unknown',
                    'teamHome': first.get('name', 'Fighter 1'),
                    'teamAway': second.get('name', 'Fighter 2'),
                    'scoreHome': '-',
                    'scoreAway': '-',
                    'eventDate': item.get('date'),
                    'venue': 'N/A',
                    'status': 'live' if status_val in ('In Progress', 'Fighting') else ('completed' if status_val in ('Finished', 'Completed') else 'scheduled'),
                    'streamUrl': '',
                    'thumbnailUrl': league.get('logo') if isinstance(league, dict) else None,
                    'countryCode': None,
                    'isLive': status_val in ('In Progress', 'Fighting'),
                    'isActive': True
                })
            except Exception as e:
                print(f"[Sports] Error parsing MMA fight: {e}")
                continue
        return events

    @staticmethod
    def _map_status(api_status):
        """Map API status to our internal status"""
        # Convert numeric status codes (NBA v2) to string equivalents
        if isinstance(api_status, int):
            if api_status == 2:
                return 'live'
            elif api_status == 3:
                return 'completed'
            else:
                return 'scheduled'

        live_statuses = [
            '1H', '2H', 'HT', 'ET', 'P', 'LIVE', 'BT',  # Football
            'Q1', 'Q2', 'Q3', 'Q4', 'OT',                 # Basketball / NFL
            'IN',                                            # Baseball/Cricket
            'S1', 'S2', 'S3', 'S4', 'S5',                  # Volleyball/Tennis sets
            'I1', 'I2', 'I3', 'I4', 'I5', 'I6', 'I7', 'I8', 'I9',  # Baseball innings
        ]
        finished_statuses = ['FT', 'AET', 'PEN', 'AOT', 'AP',
                            'GAME_FINISHED', 'POST']
        postponed_statuses = ['PST', 'CANC', 'ABD', 'WO', 'INT', 'SUSP']
        not_started = ['NS', 'TBD', 'PST']
        
        if api_status in live_statuses:
            return 'live'
        elif api_status in finished_statuses:
            return 'completed'
        elif api_status in postponed_statuses:
            return 'postponed'
        elif api_status in not_started:
            return 'scheduled'
        else:
            return 'scheduled'



