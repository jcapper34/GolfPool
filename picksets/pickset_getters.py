from typing import List
from appexceptions import PicksetNotFoundException

from helper.helpers import CURRENT_YEAR, resolve_photo
from picksets.pickset import Pickset
from players.player import Player

from players.players_helper import level_separate
from db.connection_pool import db_pool

def get_all_picks(year, separate=False) -> List[Pickset]:
    # Parameters: year
    # Returns: psid, psname, pid, pl.name, level
    GET_ALL_PICKS_QUERY = """
        SELECT ps.id AS psid, (pa.name || COALESCE(' - ' || ps.num, '')) AS psname, px.player_id AS pid, pl.name, COALESCE(lx.level, 4) AS level
            FROM picks_xref AS px
            JOIN pickset AS ps
                ON px.pickset_id = ps.id
            JOIN participant AS pa
                ON ps.participant_id = pa.id
            JOIN player AS pl
                ON px.player_id = pl.id
            LEFT JOIN level_xref AS lx
                ON px.player_id = lx.player_id AND ps.season_year = lx.season_year
            WHERE ps.season_year = %s
            ORDER BY psname, level, pl.name
            """
    results = None
    with db_pool.get_conn() as conn:
        results = conn.exec_fetch(GET_ALL_PICKS_QUERY, (year,))
    
    if not results:
        return []

    # Makes a mapping of picks to pickset
    pickset_map = {}
    for row in results:
        player = Player(id=row['pid'], name=row['name'],
                        level=row['level'])
        psid = row['psid']
        if pickset_map.get(psid) is None:
            pickset_map[psid] = Pickset(
                id=psid, name=row['psname'], picks=[player])
        else:
            pickset_map[psid].picks.append(player)

    pickset_list = list(pickset_map.values())

    if separate:
        picksets = []
        for ps in pickset_list:
            ps.picks = level_separate(ps.picks)
            picksets.append(ps)
        return picksets

    return pickset_list


def get_tournament_history(psid, year=CURRENT_YEAR) -> List:
    """
    Parameters: season_year, ps.id
    Returns: tournament.name, pos, points
    """
    GET_TOURNAMENT_HISTORY_QUERY = """
        SELECT t.name, esx.position AS pos, esx.points FROM event_standings_xref AS esx
            JOIN tournament AS t
                ON t.id = esx.tournament_id
            WHERE esx.pickset_id = %s
        """
    with db_pool.get_conn() as conn:
        return conn.exec_fetch(
            GET_TOURNAMENT_HISTORY_QUERY, (psid,))


def get_pickset(psid) -> Pickset:
    """
    Parameters: ps.id
    Returns: 
    """
    GET_PICKSET_QUERY = """
        SELECT pa.name, pa.email, ps.pin FROM participant as pa
            JOIN pickset ps
            ON ps.participant_id = pa.id
            WHERE ps.id = %s
    """
    with db_pool.get_conn() as conn:
        results = conn.exec_fetch(GET_PICKSET_QUERY, (psid,), fetchall=False)
        if not results or results is None:
            raise PicksetNotFoundException()
        
        return Pickset(id=psid, name=results['name'], email=results['email'], pin=results['pin'])
    

def get_picks(psid=None, separate=True) -> List:
    """
    Parameters: ps.id
    Returns: pid, pl.name, level, psname, pa.email, ps.pin
    """
    GET_PICKS_QUERY = """
        SELECT pl.id AS pid, pl.name, COALESCE(lx.level, 4) AS level, pl.photo_url, pl.tour_id, (pa.name || COALESCE(' - ' || ps.num, '')) AS psname, pa.email, ps.pin FROM picks_xref AS px
            JOIN player pl
            ON px.player_id = pl.id
            JOIN pickset ps
            ON px.pickset_id = ps.id
            JOIN participant pa
            ON pa.id = ps.participant_id
            LEFT JOIN level_xref lx
            ON pl.id = lx.player_id AND ps.season_year = lx.season_year
            WHERE ps.id = %s ORDER BY lx.level
    """
    picks = None
    with db_pool.get_conn() as conn:
        results = conn.exec_fetch(GET_PICKS_QUERY, (psid,))

        picks = [Player(row['pid'], name=row['name'], level=row['level'],
                photo_url=resolve_photo(row['photo_url'], row['tour_id']))
                    for row in results]
    
    if not separate:
        return picks

    return level_separate(picks)


def get_most_picked(year) -> List[Player]:
    # Parameters: year
    # Returns: id, name, num_picked, lev ORDERED BY num_picked
    GET_MOST_PICKED_QUERY = """
        SELECT pl.id, pl.name, COUNT(*) AS num_picked, COALESCE(lx.level, 4) AS lev FROM player AS pl
            JOIN picks_xref as pi ON pl.id = pi.player_id
            JOIN pickset ps on pi.pickset_id = ps.id
            LEFT JOIN level_xref lx on pl.id = lx.player_id AND ps.season_year = lx.season_year
        WHERE ps.season_year = %s
        GROUP BY pl.id, pl.name, lev
        ORDER BY num_picked DESC
    """
    results = None
    with db_pool.get_conn() as conn:
        results = conn.exec_fetch(GET_MOST_PICKED_QUERY, (year,))
    
    return [Player(id=row['id'], name=row['name'], level=row['lev'], num_picked=row['num_picked']) for row in results]


def get_login(email, pin) -> int:
    # Parameters: email, pin, year
    # Returns: ps.id
    GET_LOGIN_QUERY = """
        SELECT ps.id FROM participant AS pa
            JOIN pickset ps on pa.id = ps.participant_id
            WHERE pa.email = %s AND ps.pin = %s AND ps.season_year = %s
            LIMIT 1
    """
    with db_pool.get_conn() as conn:
        # Remember to change year
        result = conn.exec_fetch(GET_LOGIN_QUERY, (email, pin, CURRENT_YEAR))

        if conn.cur.rowcount == 0:
            return False

        return result[0][0]


def get_email_pin(email) -> str:
    EMAIL_EXISTS_QUERY = "SELECT pin FROM participant WHERE email=%s LIMIT 1"
    
    with db_pool.get_conn() as conn:
        result = conn.exec_fetch(EMAIL_EXISTS_QUERY, (email, ), fetchall=False)

        return result
