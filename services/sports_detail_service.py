"""
Sports Detail Service
Proxies enriched match data from API-Sports: events timeline, statistics,
lineups, standings, H2H, and predictions.

All calls are cached in Redis to respect rate limits.
"""

import os
import requests
from services.settings_service import get_setting_secure
from datetime import datetime
from extensions import cache

API_KEY = get_setting_secure('API_SPORTS_KEY')

# Sport-key → API base URL mapping (matches SportsCategory.api_url)
SPORT_URLS = {
    'football':   'https://v3.football.api-sports.io',
    'basketball': 'https://v1.basketball.api-sports.io',
    'baseball':   'https://v1.baseball.api-sports.io',
    'nba':        'https://v2.nba.api-sports.io',
    'nfl':        'https://v1.american-football.api-sports.io',
    'rugby':      'https://v1.rugby.api-sports.io',
    'hockey':     'https://v1.hockey.api-sports.io',
    'afl':        'https://v1.afl.api-sports.io',
    'handball':   'https://v1.handball.api-sports.io',
    'volleyball': 'https://v1.volleyball.api-sports.io',
    'formula-1':  'https://v1.formula-1.api-sports.io',
    'mma':        'https://v1.mma.api-sports.io',
}


def _headers(sport_key):
    base = SPORT_URLS.get(sport_key, '')
    host = base.replace('https://', '').split('/')[0] if base else ''
    return {
        'x-rapidapi-host': host,
        'x-rapidapi-key': API_KEY or '',
    }


def _api_get(sport_key, path, params, timeout=12):
    """Generic GET helper — returns response.json()['response'] or []."""
    base = SPORT_URLS.get(sport_key)
    if not base or not API_KEY:
        return []
    url = f"{base}{path}"
    try:
        r = requests.get(url, headers=_headers(sport_key), params=params, timeout=timeout)
        r.raise_for_status()
        data = r.json()
        if data.get('errors') and len(data['errors']) > 0:
            err = data['errors']
            print(f"[SportsDetail] API errors ({sport_key}{path}): {err}")
            # If rate-limited, surface it so the frontend can display the message
            if isinstance(err, dict) and 'requests' in err:
                return {'_error': 'API daily request limit reached. Data will be available when the limit resets.'}
        return data.get('response', [])
    except Exception as e:
        print(f"[SportsDetail] Error {sport_key}{path}: {e}")
        return []


# ──────────────────────────────
# Try DB category URL first, fallback to hardcoded
# ──────────────────────────────

def _resolve_sport(sport_key):
    """Ensure SPORT_URLS has fresh api_url from DB if possible."""
    try:
        from models.media import SportsCategory
        cat = SportsCategory.query.filter_by(key=sport_key, is_active=True).first()
        if cat and cat.api_url:
            SPORT_URLS[sport_key] = cat.api_url.rstrip('/')
    except Exception:
        pass


# ═══════════════════════════════════════
#  Phase 1 – Match Detail (events, stats, lineups)
# ═══════════════════════════════════════

def get_match_detail(sport_key, api_id):
    """
    Fetch enriched detail for a single match / fixture.
    Returns dict with keys: events, statistics, lineups, periods, players, error
    (some may be empty depending on the sport).
    """
    _resolve_sport(sport_key)
    cache_key = f"match_detail:{sport_key}:{api_id}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    result = {
        'events': [],
        'statistics': [],
        'lineups': [],
        'periods': [],
        'players': [],
        'error': None,
    }

    if sport_key == 'football':
        events_data = _football_events(api_id)
        stats_data = _football_statistics(api_id)
        lineups_data = _football_lineups(api_id)
        # Check for rate-limit error
        for d in [events_data, stats_data, lineups_data]:
            if isinstance(d, dict) and d.get('_error'):
                result['error'] = d['_error']
                cache.set(cache_key, result, timeout=30)
                return result
        result['events'] = events_data
        result['statistics'] = stats_data
        result['lineups'] = lineups_data
    elif sport_key in ('basketball', 'handball', 'volleyball', 'rugby', 'hockey'):
        team_data = _game_team_stats(sport_key, api_id)
        player_data = _game_player_stats(sport_key, api_id)
        for d in [team_data, player_data]:
            if isinstance(d, dict) and d.get('_error'):
                result['error'] = d['_error']
                cache.set(cache_key, result, timeout=30)
                return result
        result['statistics'] = team_data
        result['players'] = player_data
    elif sport_key == 'nba':
        team_data = _nba_team_stats(api_id)
        player_data = _nba_player_stats(api_id)
        for d in [team_data, player_data]:
            if isinstance(d, dict) and d.get('_error'):
                result['error'] = d['_error']
                cache.set(cache_key, result, timeout=30)
                return result
        result['statistics'] = team_data
        result['players'] = player_data
    elif sport_key == 'baseball':
        team_data = _game_team_stats(sport_key, api_id)
        if isinstance(team_data, dict) and team_data.get('_error'):
            result['error'] = team_data['_error']
            cache.set(cache_key, result, timeout=30)
            return result
        result['statistics'] = team_data
    elif sport_key == 'nfl':
        nfl_data = _nfl_stats(api_id)
        if isinstance(nfl_data, dict) and nfl_data.get('_error'):
            result['error'] = nfl_data['_error']
            cache.set(cache_key, result, timeout=30)
            return result
        result['statistics'] = nfl_data
    # Formula-1, MMA — no per-race stats endpoint on free tier

    cache.set(cache_key, result, timeout=60)
    return result


# ── Football specifics ──

def _football_events(fixture_id):
    """Match timeline: goals, cards, subs (Football v3)"""
    raw = _api_get('football', '/fixtures/events', {'fixture': fixture_id})
    if isinstance(raw, dict) and raw.get('_error'):
        return raw
    out = []
    for e in raw:
        out.append({
            'time':   e.get('time', {}).get('elapsed'),
            'extra':  e.get('time', {}).get('extra'),
            'team':   e.get('team', {}).get('name'),
            'teamId': e.get('team', {}).get('id'),
            'player': e.get('player', {}).get('name'),
            'assist': e.get('assist', {}).get('name'),
            'type':   e.get('type'),          # Goal, Card, subst, Var
            'detail': e.get('detail'),         # Normal Goal, Yellow Card, etc.
            'comments': e.get('comments'),
        })
    return out


def _football_statistics(fixture_id):
    """Team-level stats (Football v3)"""
    raw = _api_get('football', '/fixtures/statistics', {'fixture': fixture_id})
    if isinstance(raw, dict) and raw.get('_error'):
        return raw
    out = []
    for team_block in raw:
        team_info = team_block.get('team', {})
        stats_list = team_block.get('statistics', [])
        stats_map = {}
        for s in stats_list:
            stats_map[s.get('type', '')] = s.get('value')
        out.append({
            'team':   team_info.get('name'),
            'teamId': team_info.get('id'),
            'logo':   team_info.get('logo'),
            'stats':  stats_map,
        })
    return out


def _football_lineups(fixture_id):
    """Lineups & formation (Football v3)"""
    raw = _api_get('football', '/fixtures/lineups', {'fixture': fixture_id})
    if isinstance(raw, dict) and raw.get('_error'):
        return raw
    out = []
    for lineup in raw:
        team_info = lineup.get('team', {})
        coach = lineup.get('coach', {})
        starters = []
        subs = []
        for p in lineup.get('startXI', []):
            pl = p.get('player', {})
            starters.append({
                'id': pl.get('id'),
                'name': pl.get('name'),
                'number': pl.get('number'),
                'pos': pl.get('pos'),
                'grid': pl.get('grid'),
            })
        for p in lineup.get('substitutes', []):
            pl = p.get('player', {})
            subs.append({
                'id': pl.get('id'),
                'name': pl.get('name'),
                'number': pl.get('number'),
                'pos': pl.get('pos'),
            })
        out.append({
            'team':      team_info.get('name'),
            'teamId':    team_info.get('id'),
            'logo':      team_info.get('logo'),
            'formation': lineup.get('formation'),
            'coach':     coach.get('name'),
            'startXI':   starters,
            'substitutes': subs,
        })
    return out


# ── Generic game sports (basketball, handball, volleyball, rugby, hockey) ──

def _game_team_stats(sport_key, game_id):
    """Team statistics for game-based sports"""
    path = '/statistics' if sport_key in ('hockey',) else '/games/statistics/teams'
    # Hockey uses /statistics?game=, others use /games/statistics/teams?id=
    if sport_key == 'hockey':
        raw = _api_get(sport_key, '/statistics', {'game': game_id})
    else:
        raw = _api_get(sport_key, '/games/statistics/teams', {'id': game_id})
    if isinstance(raw, dict) and raw.get('_error'):
        return raw
    out = []
    for item in raw:
        team = item.get('team', {})
        stats = item.get('statistics', [])
        if isinstance(stats, list):
            stats_map = {}
            for s in stats:
                if isinstance(s, dict):
                    stats_map[s.get('type', '')] = s.get('value')
            stats = stats_map
        out.append({
            'team':   team.get('name'),
            'teamId': team.get('id'),
            'logo':   team.get('logo'),
            'stats':  stats if isinstance(stats, dict) else {},
        })
    return out


def _game_player_stats(sport_key, game_id):
    """Player statistics for basketball/handball/volleyball"""
    raw = _api_get(sport_key, '/games/statistics/players', {'id': game_id})
    if isinstance(raw, dict) and raw.get('_error'):
        return raw
    out = []
    for item in raw:
        team = item.get('team', {})
        players = item.get('players', [])
        team_players = []
        for p in players:
            player = p.get('player', {}) if isinstance(p, dict) else {}
            stats = p.get('statistics', {}) if isinstance(p, dict) else {}
            team_players.append({
                'id': player.get('id'),
                'name': player.get('name'),
                'stats': stats if isinstance(stats, dict) else {},
            })
        out.append({
            'team':    team.get('name'),
            'teamId':  team.get('id'),
            'players': team_players,
        })
    return out


# ── NBA specifics ──

def _nba_team_stats(game_id):
    """NBA v2 team stats"""
    raw = _api_get('nba', '/games/statistics', {'id': game_id})
    if isinstance(raw, dict) and raw.get('_error'):
        return raw
    out = []
    for item in raw:
        team = item.get('team', {})
        stats_list = item.get('statistics', [])
        stats = stats_list[0] if stats_list else {}
        out.append({
            'team':   team.get('name'),
            'teamId': team.get('id'),
            'logo':   team.get('logo'),
            'stats':  stats if isinstance(stats, dict) else {},
        })
    return out


def _nba_player_stats(game_id):
    """NBA v2 player stats"""
    raw = _api_get('nba', '/players/statistics', {'game': game_id})
    if isinstance(raw, dict) and raw.get('_error'):
        return raw
    # NBA v2 returns flat list of player stats
    team_map = {}
    for item in raw:
        team = item.get('team', {})
        tname = team.get('name', 'Unknown')
        player = item.get('player', {})
        if tname not in team_map:
            team_map[tname] = {'team': tname, 'teamId': team.get('id'), 'players': []}
        team_map[tname]['players'].append({
            'id': player.get('id'),
            'name': f"{player.get('firstname', '')} {player.get('lastname', '')}".strip(),
            'stats': {
                'points': item.get('points'),
                'assists': item.get('assists'),
                'rebounds': item.get('totReb'),
                'steals': item.get('steals'),
                'blocks': item.get('blocks'),
                'turnovers': item.get('turnovers'),
                'minutes': item.get('min'),
                'fgm': item.get('fgm'),
                'fga': item.get('fga'),
                'fgp': item.get('fgp'),
                'tpm': item.get('tpm'),
                'tpa': item.get('tpa'),
                'ftm': item.get('ftm'),
                'fta': item.get('fta'),
                'plusMinus': item.get('plusMinus'),
            },
        })
    return list(team_map.values())


# ── NFL ──

def _nfl_stats(game_id):
    """American Football team stats"""
    raw = _api_get('nfl', '/games/statistics/teams', {'id': game_id})
    if isinstance(raw, dict) and raw.get('_error'):
        return raw
    out = []
    for item in raw:
        team = item.get('team', {})
        groups = item.get('groups', [])
        stats = {}
        for grp in groups:
            grp_name = grp.get('name', '')
            for s in grp.get('statistics', []):
                stats[f"{grp_name} - {s.get('name', '')}"] = s.get('value')
        out.append({
            'team':   team.get('name'),
            'teamId': team.get('id'),
            'logo':   team.get('logo'),
            'stats':  stats,
        })
    return out


# ═══════════════════════════════════════
#  Phase 2 – Standings
# ═══════════════════════════════════════

def get_standings(sport_key, league_id, season=None):
    """
    Fetch league standings.
    Returns list of groups/tables.
    """
    _resolve_sport(sport_key)
    if not season:
        season = datetime.now().year

    cache_key = f"standings:{sport_key}:{league_id}:{season}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    params = {'league': league_id, 'season': season}

    if sport_key == 'football':
        raw = _api_get('football', '/standings', params)
    elif sport_key == 'nba':
        raw = _api_get('nba', '/standings', {'league': 'standard', 'season': season})
    elif sport_key in ('basketball', 'baseball', 'rugby', 'hockey', 'handball', 'volleyball'):
        raw = _api_get(sport_key, '/standings', params)
    elif sport_key == 'nfl':
        raw = _api_get('nfl', '/standings', params)
    else:
        raw = []

    result = _transform_standings(sport_key, raw)
    cache.set(cache_key, result, timeout=3600)
    return result


def _transform_standings(sport_key, raw):
    """Normalize standings across sports into a common format."""
    if sport_key == 'football':
        # Football v3: [{league:{standings:[[{rank,team,points,...},...]]}}]
        groups = []
        for item in raw:
            league = item.get('league', {})
            for table in league.get('standings', []):
                rows = []
                for row in table:
                    team = row.get('team', {})
                    all_stats = row.get('all', {})
                    rows.append({
                        'rank': row.get('rank'),
                        'team': team.get('name'),
                        'teamId': team.get('id'),
                        'logo': team.get('logo'),
                        'points': row.get('points'),
                        'played': all_stats.get('played'),
                        'won': all_stats.get('win'),
                        'drawn': all_stats.get('draw'),
                        'lost': all_stats.get('lose'),
                        'goalsFor': all_stats.get('goals', {}).get('for'),
                        'goalsAgainst': all_stats.get('goals', {}).get('against'),
                        'goalDiff': row.get('goalsDiff'),
                        'form': row.get('form'),
                        'description': row.get('description'),
                    })
                groups.append({
                    'name': row.get('group', league.get('name', '')) if table else league.get('name', ''),
                    'rows': rows,
                })
        return groups

    elif sport_key == 'nba':
        # NBA v2: flat list [{team:{name,logo},conference:{name},win:{total},loss:{total},...}]
        conf_map = {}
        for row in raw:
            team = row.get('team', {})
            conf = row.get('conference', {}).get('name', 'Unknown')
            win = row.get('win', {})
            loss = row.get('loss', {})
            if conf not in conf_map:
                conf_map[conf] = []
            conf_map[conf].append({
                'rank': row.get('conference', {}).get('rank'),
                'team': team.get('name'),
                'teamId': team.get('id'),
                'logo': team.get('logo'),
                'won': win.get('total'),
                'lost': loss.get('total'),
                'winPct': win.get('percentage'),
                'streak': row.get('streak'),
                'gamesBehind': row.get('gamesBehind'),
            })
        return [{'name': conf, 'rows': sorted(rows, key=lambda x: x.get('rank') or 999)} for conf, rows in conf_map.items()]

    else:
        # Generic: most sports return [{position,team:{name,id,logo},points,games:{...},group:{name}}]
        group_map = {}
        for row in raw:
            team = row.get('team', {})
            group_name = row.get('group', {}).get('name', 'Standings') if isinstance(row.get('group'), dict) else 'Standings'
            games = row.get('games', {})
            if group_name not in group_map:
                group_map[group_name] = []
            group_map[group_name].append({
                'rank': row.get('position'),
                'team': team.get('name'),
                'teamId': team.get('id'),
                'logo': team.get('logo'),
                'points': row.get('points'),
                'played': games.get('played'),
                'won': games.get('win', {}).get('total') if isinstance(games.get('win'), dict) else games.get('win'),
                'drawn': games.get('draw', {}).get('total') if isinstance(games.get('draw'), dict) else games.get('draw'),
                'lost': games.get('lose', {}).get('total') if isinstance(games.get('lose'), dict) else games.get('lose'),
                'form': row.get('form'),
                'description': row.get('description'),
            })
        return [{'name': g, 'rows': rows} for g, rows in group_map.items()]


# ═══════════════════════════════════════
#  Phase 3 – Head-to-Head
# ═══════════════════════════════════════

def get_h2h(sport_key, team1_id, team2_id):
    """Fetch head-to-head past matches between two teams."""
    _resolve_sport(sport_key)
    cache_key = f"h2h:{sport_key}:{team1_id}-{team2_id}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    h2h_str = f"{team1_id}-{team2_id}"

    if sport_key == 'football':
        raw = _api_get('football', '/fixtures/headtohead', {'h2h': h2h_str, 'last': 10})
    elif sport_key == 'nba':
        # NBA v2 doesn't have a dedicated H2H endpoint — use games?h2h=
        raw = _api_get('nba', '/games', {'h2h': h2h_str, 'season': datetime.now().year})
    elif sport_key in ('basketball', 'baseball', 'rugby', 'hockey', 'handball', 'volleyball'):
        raw = _api_get(sport_key, '/games/h2h', {'h2h': h2h_str, 'last': 10})
    else:
        raw = []

    from services.api_sports_service import APISportsService
    result = APISportsService._transform_response(raw, sport_key.title(), sport_key)
    cache.set(cache_key, result, timeout=3600)
    return result


# ═══════════════════════════════════════
#  Phase 4 – Predictions (Football only, free tier)
# ═══════════════════════════════════════

def get_predictions(sport_key, fixture_id):
    """Fetch match prediction (Football v3 only on free tier)."""
    _resolve_sport(sport_key)
    if sport_key != 'football':
        return None

    cache_key = f"prediction:{fixture_id}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    raw = _api_get('football', '/predictions', {'fixture': fixture_id})
    if not raw:
        return None

    item = raw[0] if raw else {}
    predictions = item.get('predictions', {})
    comparison = item.get('comparison', {})
    teams = item.get('teams', {})

    result = {
        'winner': {
            'id': predictions.get('winner', {}).get('id'),
            'name': predictions.get('winner', {}).get('name'),
            'comment': predictions.get('winner', {}).get('comment'),
        },
        'winOrDraw': predictions.get('win_or_draw'),
        'underOver': predictions.get('under_over'),
        'goals': predictions.get('goals', {}),
        'advice': predictions.get('advice'),
        'percent': predictions.get('percent', {}),
        'comparison': comparison,
        'teams': {
            'home': {
                'name': teams.get('home', {}).get('name'),
                'logo': teams.get('home', {}).get('logo'),
                'lastFive': teams.get('home', {}).get('last_5', {}),
                'league': teams.get('home', {}).get('league', {}),
            },
            'away': {
                'name': teams.get('away', {}).get('name'),
                'logo': teams.get('away', {}).get('logo'),
                'lastFive': teams.get('away', {}).get('last_5', {}),
                'league': teams.get('away', {}).get('league', {}),
            },
        },
    }

    cache.set(cache_key, result, timeout=3600)
    return result
