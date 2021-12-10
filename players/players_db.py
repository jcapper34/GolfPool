from db.db_helper import filter_conn
from players.player import Player
from players.players_helper import level_separate


# Parameters: year
# Returns: lx.player_id, pl.name, lx.level, pl.photo_url
GET_LEVELS_QUERY = """
                SELECT lx.player_id AS player_id, pl.name, lx.level, pl.photo_url FROM level_xref AS lx
                    JOIN player AS pl ON pl.id = lx.player_id
                WHERE lx.season_year = %s
            """
def get_levels(year, separate=True, conn=None):
    conn = filter_conn(conn)
    results = conn.exec_fetch(GET_LEVELS_QUERY, (year,))
    players = [Player(id=row['player_id'], name=row['name'], level=row['level'], photo_url=Player.PGA_PHOTO_URL % row['photo_url']) for row in results]

    if separate:
        return level_separate(players)

    return players
