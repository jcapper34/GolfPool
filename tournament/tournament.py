from pprint import pprint

from db.db_helper import filter_conn
from helper import func_find, CURRENT_YEAR
from picksets.pickset import Pickset
from players.player import Player


class Tournament:
    # Golf Channel URL
    LEADERBOARD_URL = "https://www.golfchannel.com/api/v2/events/%s/leaderboard" # Parameters: tournament_id

    def __init__(self, tid=None, year=None, tournament_name=None):
        self.tid = tid
        self.year = year
        self.name = tournament_name

        self.players = []
        self.picksets = []

    ### DATABASE FILLS ###

    # Parameters: year, tid
    # Returns: pid, name, points, pos ORDERED BY points
    GET_DB_RANKINGS_QUERY = """
    WITH leaderboard AS (SELECT pl.id AS pid, pl.name, SUM(elx.points) as points, RANK() OVER(ORDER BY SUM(elx.points) DESC) AS pos FROM event_leaderboard_xref AS elx
      JOIN event
        ON event.tournament_id = elx.tournament_id AND event.season_year = elx.season_year
      JOIN tournament AS t
          ON t.id = event.tournament_id
      JOIN player AS pl
        ON pl.id = elx.player_id
      WHERE event.season_year = %s AND elx.tournament_id = COALESCE(%s, elx.tournament_id)
      GROUP BY pid, pl.name)
      SELECT * FROM leaderboard WHERE points > 0
                          """
    def fill_db_rankings(self, year, tid, conn=None):
        conn = filter_conn(conn)
        if tid == 'cumulative': tid = None

        raw_players = conn.exec_fetch(Tournament.GET_DB_RANKINGS_QUERY, (year, tid))
        if not raw_players:
            return False

        self.players = [Player(**p) for p in raw_players]

        # Associate tournament names
        tournament_names = {
            "014": "The Masters",
            "026": "U.S Open",
            "100": "British Open",
            "033": "PGA Championship"
        }

        self.tid = "cumulative" if tid is None else tid
        self.name = "Cumulative" if tid is None else tournament_names[tid]
        self.year = year

        return True

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
    def fill_db_standings(self, year, tid, conn=None):
        conn = filter_conn(conn)
        if tid == 'cumulative': tid = None

        results = conn.exec_fetch(Tournament.GET_DB_STANDINGS_QUERY, (year, tid))
        if not results:
            return False

        self.picksets = [Pickset(psid=row['psid'], name=row['name'], points=row['points'], pos=row['pos']) for row in results]

        return True

    """ API FILLS """
    def api_fill(self, tid='live', year=CURRENT_YEAR):
        self.tid = tid
        self.year = year

    ### CALCULATIONS ###

    """ MERGES """
    def merge_all_picks(self, all_picks):
        for pickset in self.picksets:
            ps2 = func_find(all_picks, lambda ps: ps.id == pickset.id)
            pickset.picks = ps2.picks