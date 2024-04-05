from typing import Dict, Tuple, List
from db.connection_pool import db_pool
from helper.helpers import CURRENT_YEAR, resolve_photo
from picksets.pickset import Pickset
from players.player import Player
from players.players_helper import level_separate


# Parameters: year
# Returns: lx.player_id, pl.name, lx.level, pl.photo_url
GET_LEVELS_QUERY = """
                SELECT lx.player_id AS player_id, pl.name, lx.level, pl.photo_url, pl.tour_id FROM level_xref AS lx
                    JOIN player AS pl ON pl.id = lx.player_id
                WHERE lx.season_year = %s
            """
def get_levels_db(year, separate=True) -> List:
    players = None
    with db_pool.get_conn() as conn:
        results = conn.exec_fetch(GET_LEVELS_QUERY, (year,))
        players = [Player(
            id=row['player_id'], 
            name=row['name'], 
            level=row['level'], 
            photo_url=resolve_photo(row['photo_url'], row['tour_id'])) for row in results]

    if separate:
        return level_separate(players)

    return players

# Parameters: year
# Returns: pick_limit
GET_LEVEL_LIMITS_QUERY = """
    SELECT pick_limit FROM level_limit_xref WHERE season_year = %s
"""
def get_level_limits(year) -> List:
    with db_pool.get_conn() as conn:
        return [r[0] for r in conn.exec_fetch(GET_LEVEL_LIMITS_QUERY, (year,))]


GET_NON_LEVELED_PLAYERS_QUERY = """
    SELECT pl.id, pl.name FROM player AS pl 
    WHERE NOT EXISTS (SELECT FROM level_xref WHERE player_id = pl.id AND season_year = %s)
"""
def get_non_leveled_players(year) -> List:
    with db_pool.get_conn() as conn:
        return [dict(pl) for pl in conn.exec_fetch(GET_NON_LEVELED_PLAYERS_QUERY, (year,))]

# Parameters: pid, year
# Returns: pos, score, points, tid, thru, photo_url
GET_TOURNAMENT_DATA_QUERY = """
SELECT position AS pos, score AS total, points, tournament_id AS tid, 18 AS thru, p.photo_url, p.tour_id FROM event_leaderboard_xref AS elx
    JOIN player p on elx.player_id = p.id
    WHERE p.id = %s AND elx.season_year=%s
"""
def get_tournament_player_db(pid, year) -> Tuple[Dict]:    
    player = Player(id=pid)
    
    all_tournament_results = None
    with db_pool.get_conn() as conn:
        all_tournament_results = list(conn.exec_fetch(GET_TOURNAMENT_DATA_QUERY, (pid, year)))

    # tournament_results = dict(func_find(all_tournament_results, lambda t: t['tid'] == tid))
    # del tournament_results['tid']   # Don't need this property anymore
    
    return tuple(dict(t) for t in all_tournament_results)


# Parameters: pid, year
# Returns: psid, name
GET_WHO_PICKED_QUERY = """SELECT ps.id AS psid, (pa.name || COALESCE(' - ' || ps.num, '')) AS name FROM pickset AS ps
                    JOIN picks_xref px on ps.id = px.pickset_id
                    JOIN participant pa on ps.participant_id = pa.id
                    WHERE px.player_id = %s AND ps.season_year = %s
                    ORDER BY name"""
def who_picked_player(pid, year=CURRENT_YEAR) -> List[Pickset]:
    picked_by = None
    with db_pool.get_conn() as conn:
        results = conn.exec_fetch(GET_WHO_PICKED_QUERY, (pid, year))
        picked_by = [Pickset(id=row['psid'], name=row['name']) for row in results]

    return picked_by


def get_player_photo(pid) -> str:
    with db_pool.get_conn() as conn:
        result = conn.exec_fetch(
            "SELECT photo_url, tour_id FROM player WHERE id=%s", (pid,), fetchall=False)
        
        return resolve_photo(result['photo_url'], result['tour_id'])