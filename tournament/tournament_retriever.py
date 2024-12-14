from datetime import datetime
from typing import List
import logging

from config import LEADERBOARD_URL, OWGR_LEADERBOARD_URL, POINT_MAP
from db.database_connection import DatabaseConnection
from helper.globalcache import GlobalCache
from helpers import func_find, request_json
from picksets.pickset import Pickset
from players.player import Player
from tournament.tournament import Tournament
from db.connection_pool import db_pool


def get_player_thru(leaderboard_player, current_round):
    if current_round is not None:
        player_round = func_find(leaderboard_player.get("PlayerRounds", []), 
                lambda r: r["sequence"] == current_round["number"])
        
        if player_round is not None:
            return player_round["thru"]
    
    return None


def get_api_tournament(golfcom_tid, year=None, tournament_name=None) -> Tournament:
    url = LEADERBOARD_URL % golfcom_tid

    logging.info("[get_api_tournament] Fetching %s", url)
    api_data = request_json(url)
    if api_data is None:
        return None # Tournament has no results

    api_tournament = api_data['data']
    leaderboard = api_tournament['leaderboard']

    tournament = Tournament()
    tournament.name = tournament_name
    tournament.golfcom_tid = golfcom_tid
    tournament.scorecards = api_tournament.get('scorecards', [])
    tournament.year = year

    rounds = api_tournament.get("roundStatus", [])

    current_round = func_find(rounds, lambda x: x.get("status") == "inprogress" or x.get("status") == "delayed")
    common_thru = None
    if current_round is None and all([r["status"] == "closed" for r in rounds]):
            common_thru = 18

    tournament.players = [Player(id=str(pl['playerId']),
                                 name=' '.join([pl['Player']['firstName'], pl['Player']['lastName']]),
                                 pos=pl['position'],
                                 points=POINT_MAP[str(
                                     pl['position'])] if pl['position'] is not None and pl['position'] <= 20 else 0,
                                 raw_pos=pl['position'],
                                 total=pl['score'],
                                 thru=common_thru if common_thru is not None else get_player_thru(pl, current_round),
                                #  photo_url=pl['imageUrl'],
                                 status=pl['playerStatus']
                                 ) for pl in leaderboard]  # Create Player objects of leaderboard

    # Sort so that None is at the end
    tournament.players.sort(key=lambda x: (x.raw_pos is None, x.raw_pos))

    return tournament


def get_db_rankings(tid, year) -> List[Player]:
    # Parameters: year, tid
    # Returns: pid, name, points, pos ORDERED BY points
    GET_DB_RANKINGS_QUERY = """
    WITH leaderboard AS (SELECT pl.id, pl.name, SUM(elx.points) as points, RANK() OVER(ORDER BY SUM(elx.points) DESC) AS pos FROM event_leaderboard_xref AS elx
        JOIN event
            ON event.tournament_id = elx.tournament_id AND event.season_year = elx.season_year
        JOIN tournament AS t
            ON t.id = event.tournament_id
        JOIN player AS pl
            ON pl.id = elx.player_id
        WHERE event.season_year = ? AND elx.tournament_id = COALESCE(?, elx.tournament_id)
        GROUP BY pl.id, pl.name)
        SELECT * FROM leaderboard WHERE points > 0
    """
    
    raw_players = None
    with DatabaseConnection() as conn:
        cursor = conn.cursor()
        raw_players = cursor.execute(
            GET_DB_RANKINGS_QUERY, (year, tid if tid != 'cumulative' else None)).fetchall()
    
        if raw_players:
            return [Player(id=row['id'], name=row['name'], points=row['points'], pos=row['pos']) for row in raw_players]

    return None


def get_db_standings(tid, year, conn=None) -> List[Pickset]:
    # Parameters: year, tid
    # Returns: pos, psid, name, points ORDERED & RANKED BY pos
    GET_DB_STANDINGS_QUERY = """
        SELECT RANK() OVER(ORDER BY SUM(esx.points) DESC) AS pos, ps.id AS psid, (pa.name || COALESCE(' - ' || ps.num, '')) AS name, SUM(esx.points) AS points
            FROM event_standings_xref AS esx
                JOIN pickset AS ps
                    ON esx.pickset_id = ps.id
                JOIN participant AS pa
                    ON ps.participant_id = pa.id
            WHERE esx.season_year = ? AND esx.tournament_id = COALESCE(?, esx.tournament_id)
            GROUP BY ps.id, (pa.name || COALESCE(' - ' || ps.num, ''))
            ORDER BY SUM(esx.points) DESC
    """

    results = None
    with DatabaseConnection() as conn:
        cursor = conn.cursor()
        results = cursor.execute(GET_DB_STANDINGS_QUERY, (year, tid if tid != 'cumulative' else None)).fetchall()
    if results:
        return [Pickset(id=row['psid'], name=row['name'],
                                points=row['points'], pos=row['pos']) for row in results]

    return None


# Used to get all season years that have been stored in DB
def get_past_events(conn=None) -> dict:
    PAST_EVENTS_QUERY = """
        SELECT season_year, tournament.id, tournament.name from event 
            JOIN tournament ON event.tournament_id = tournament.id
            ORDER BY season_year DESC
    """
    results = None
    with DatabaseConnection() as conn:
        cursor = conn.cursor()
        results = cursor.execute(PAST_EVENTS_QUERY).fetchall()

    year_tourny = {}
    for row in results:
        info = {
            'id': row[1],
            'name': row[2]
        }
        if year_tourny.get(row[0]) is None:
            year_tourny[row[0]] = [info]
        else:
            year_tourny[row[0]].append(info)

    return year_tourny
