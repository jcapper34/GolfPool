from typing import Dict, Tuple
from config import PGA_PHOTO_URL
from db.db_helper import filter_conn
from helper import CURRENT_YEAR, func_find
from picksets.pickset import Pickset
from players.player import Player
from players.players_helper import level_separate


# Parameters: year
# Returns: lx.player_id, pl.name, lx.level, pl.photo_url
GET_LEVELS_QUERY = """
                SELECT lx.player_id AS player_id, pl.name, lx.level, pl.photo_url FROM level_xref AS lx
                    JOIN player AS pl ON pl.id = lx.player_id
                WHERE lx.season_year = %s
            """
def get_levels_db(year, separate=True, conn=None):
    conn = filter_conn(conn)
    results = conn.exec_fetch(GET_LEVELS_QUERY, (year,))
    players = [Player(id=row['player_id'], name=row['name'], level=row['level'], photo_url=PGA_PHOTO_URL % row['photo_url']) for row in results]

    if separate:
        return level_separate(players)

    return players


# Parameters: pid, year
# Returns: pos, score, points, tid, thru, photo_url
GET_TOURNAMENT_DATA_QUERY = """
SELECT position AS pos, score AS total, points, tournament_id AS tid, 18 AS thru, p.photo_url FROM event_leaderboard_xref AS elx
    JOIN player p on elx.player_id = p.id
    WHERE p.id = %s AND elx.season_year=%s
"""
def get_tournament_player_db(pid, tid, year, conn=None) -> Dict:
    conn = filter_conn(conn)
    
    player = Player(id=pid)

    all_tournament_results = list(conn.exec_fetch(GET_TOURNAMENT_DATA_QUERY, (pid, year)))

    tournament_results = dict(func_find(all_tournament_results, lambda t: t['tid'] == tid))
    del tournament_results['tid']   # Don't need this property anymore
    
    return tournament_results


# Parameters: pid, year
# Returns: psid, name
GET_WHO_PICKED_QUERY = """SELECT ps.id AS psid, (pa.name || COALESCE(' - ' || ps.num, '')) AS name FROM pickset AS ps
                    JOIN picks_xref px on ps.id = px.pickset_id
                    JOIN participant pa on ps.participant_id = pa.id
                    WHERE px.player_id = %s AND ps.season_year = %s
                    ORDER BY name"""
def who_picked_player(pid, year=CURRENT_YEAR, conn=None):
    conn = filter_conn(conn)

    results = conn.exec_fetch(GET_WHO_PICKED_QUERY, (pid, year))

    picked_by = [Pickset(id=row['psid'], name=row['name']) for row in results]

    return picked_by
