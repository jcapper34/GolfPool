from db.conn import Conn


# GROUP FUNCTIONS #
from db.db_helper import filter_conn
from picksets.pickset import Pickset
from players.player import Player

# Parameters: year
# Returns: psid, psname, pid, pl.name, pl.level
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
def get_all_picks(year, conn=None):
    conn = filter_conn(conn)

    results = conn.exec_fetch(GET_ALL_PICKS_QUERY, (year,))

    picksets = []
    current_psid = results[0]['psid']
    current_picklist = []
    row_len = conn.cur.rowcount
    for i in range(row_len):
        row = results[i]
        player = Player(pid=row['pid'], name=row['name'], level=row['level'])
        if row['psid'] != current_psid:
            current_psid = row['psid']
            picksets.append(Pickset(psid=current_psid, name=row['psname'], picks=current_picklist))
            current_picklist = [player]
        else:
            current_picklist.append(player)
            if i == row_len - 1:
                picksets.append(Pickset(psid=current_psid, name=row['psname'], picks=current_picklist))

    return picksets


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