from db.db_helper import filter_conn
from players.player import Player
from players.players_helper import level_separate


# Parameters: year
# Returns: lx.player_id, pl.name, lx.level, pl.tour_id
GET_LEVELS_QUERY = """
                SELECT lx.player_id AS player_id, pl.name, lx.level, pl.tour_id FROM level_xref AS lx
                    JOIN player AS pl ON pl.id = lx.player_id
                WHERE lx.season_year = %s
            """
def get_levels(year, separate=True, conn=None):
    conn = filter_conn(conn)
    results = conn.exec_fetch(GET_LEVELS_QUERY, (year,))
    players = [Player(pid=row['player_id'], name=row['name'], level=row['level'], tour_id=row['tour_id']) for row in results]

    if separate:
        return level_separate(players)

    return players
