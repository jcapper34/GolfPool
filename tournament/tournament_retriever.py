from datetime import datetime
from typing import List

from config import LEADERBOARD_URL, POINT_MAP
from helper.globalcache import GlobalCache
from helper.helpers import request_json
from picksets.pickset import Pickset
from players.player import Player
from tournament.tournament import Tournament
from db.connection_pool import db_pool


def get_api_tournament(channel_tid, year=None) -> Tournament:
    channel_tid = int(channel_tid)

    api_data = request_json(LEADERBOARD_URL % channel_tid)
    api_tournament = api_data.get('result')
    if not api_tournament or api_tournament is None:
        return None # Tournament has no results

    leaderboard = api_tournament['golfers']

    tournament = Tournament()
    tournament.channel_tid = api_tournament.get('eventKey')
    tournament.scorecards = api_tournament['scorecards']

    # Try to get year from api tournament
    if year is None:
        try:
            tournament.year = datetime.strptime(
                api_data.get('latestOddsUpdate'), "%B %d, %Y").year
        except Exception:
            tournament.year = year

    tournament.players = [Player(id=str(pl['golferId']),
                                 name=pl['firstName'] + " " + pl['lastName'],
                                 pos=pl['position'] if pl['sortHelp'] is not None and pl['sortHelp'] < 1000 else None,
                                 points=POINT_MAP[str(
                                     pl['sortHelp'])] if pl['sortHelp'] is not None and pl['sortHelp'] <= 20 else 0,
                                 raw_pos=pl['sortHelp'],
                                 total=pl['overallPar'],
                                 thru=pl['thruHole'],
                                 photo_url=pl['imageUrl'],
                                 country_flag=pl['representsCountryUrl'],
                                 status=pl['status']
                                 ) for pl in leaderboard]  # Create Player objects of leaderboard

    # Sort so that None is at the end
    tournament.players.sort(key=lambda x: (x.raw_pos is None, x.raw_pos))
    tournament.name = api_tournament.get("eventName")

    return tournament


def get_db_rankings(tid, year, conn=None) -> List[Player]:
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
        WHERE event.season_year = %s AND elx.tournament_id = COALESCE(%s, elx.tournament_id)
        GROUP BY pl.id, pl.name)
        SELECT * FROM leaderboard WHERE points > 0
    """
    
    raw_players = None
    with db_pool.get_conn() as conn:
        raw_players = conn.exec_fetch(GET_DB_RANKINGS_QUERY, (
            year, tid if tid != 'cumulative' else None))

    if raw_players:
        return [Player(**p) for p in raw_players]

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
            WHERE esx.season_year = %s AND esx.tournament_id = COALESCE(%s, esx.tournament_id)
            GROUP BY ps.id, name
            ORDER BY SUM(esx.points) DESC
    """

    results = None
    with db_pool.get_conn() as conn:
        results = conn.exec_fetch(GET_DB_STANDINGS_QUERY,
                                (year, tid if tid != 'cumulative' else None))
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
    with db_pool.get_conn() as conn:
        results = conn.exec_fetch(PAST_EVENTS_QUERY)

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
