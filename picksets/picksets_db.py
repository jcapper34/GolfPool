from db.conn import Conn


# GROUP FUNCTIONS #
from db.db_helper import filter_conn
from helper import CURRENT_YEAR
from picksets.pickset import Pickset
from players.player import Player

# Parameters: year
# Returns: psid, psname, pid, pl.name, pl.level
from players.players_helper import level_separate

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
def get_all_picks(year, separate=False, conn=None):
    conn = filter_conn(conn)

    results = conn.exec_fetch(GET_ALL_PICKS_QUERY, (year,))
    if not results:
        return []

    # Makes a mapping of picks to pickset
    pickset_map = {}
    for row in results:
        player = Player(pid=row['pid'], name=row['name'], level=row['level'])
        psid = row['psid']
        if pickset_map.get(psid) is None:
            pickset_map[psid] = Pickset(psid=psid, name=row['psname'], picks=[player])
        else:
            pickset_map[psid].picks.append(player)

    pickset_list = pickset_map.values()

    if separate:
        picksets = []
        for ps in pickset_list:
            ps.picks = level_separate(ps.picks)
            picksets.append(ps)
        return picksets

    return pickset_list

    # I'll explain later lol
    # picksets = []
    # current_psid = results[0]['psid']
    # current_picklist = []
    # row_len = conn.cur.rowcount
    # for i in range(row_len):
    #     row = results[i]
    #     player = Player(pid=row['pid'], name=row['name'], level=row['level'])
    #     if row['psid'] != current_psid:
    #         current_psid = row['psid']
    #         if separate:    # Separate by level
    #             current_picklist = level_separate(current_picklist)
    #         picksets.append(Pickset(psid=current_psid, name=row['psname'], picks=current_picklist))
    #         current_picklist = [player]
    #     else:
    #         current_picklist.append(player)
    #         if i == row_len - 1:
    #             if separate:    # Separate by level
    #                 current_picklist = level_separate(current_picklist)
    #             picksets.append(Pickset(psid=current_psid, name=row['psname'], picks=current_picklist))



    # return picksets


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
def get_most_picked(year, conn=None):
    conn = filter_conn(conn)
    results = conn.exec_fetch(GET_MOST_PICKED_QUERY, (year,))
    return [Player(row['id'], row['name'], level=row['lev'], num_picked=row['num_picked']) for row in results]

# Parameters: email, pin, year
# Returns: ps.id
GET_LOGIN_QUERY = """
    SELECT ps.id FROM participant AS pa
        JOIN pickset ps on pa.id = ps.participant_id
        WHERE pa.email = %s AND pa.pin = %s AND ps.season_year = %s
        LIMIT 1
"""
def get_login(email, pin):
    conn = Conn()
    result = conn.exec_fetch(GET_LOGIN_QUERY, (email, pin, CURRENT_YEAR))   # Remember to change year

    if conn.cur.rowcount == 0:
        return False

    return result[0][0]
