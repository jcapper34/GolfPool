from db.conn import Conn
from db.db_helper import filter_conn
from players import player

class Pickset:
    ### CONSTANTS ###
    PICKS_ALLOWED = [3, 3, 2, 2]

    ### CONSTRUCTOR ###
    def __init__(self, psid, name=None, email=None, pin=None, picks=None, points=None, pos=None):
        # General Info
        self.id = psid
        self.name = name
        self.email = email
        self.pin = pin

        # Picks
        self.picks = picks

        # Tournament
        self.points = points
        self.pos = pos

    ### HELPERS ###
    def get_pids(self):
        pass

    def validate_picks(self):
        if len(self.picks) != len(Pickset.PICKS_ALLOWED):   ## Check for correct number of levels
            return False

        for i in range(len(self.picks)):
            level_players = self.picks[i]
            if len(level_players) != Pickset.PICKS_ALLOWED[i]:
                return False

        return True


    ### Database Requests ###
    # Parameters: ps.id
    # Returns: pid, pl.name, level
    GET_PICKS_QUERY = """
    SELECT pl.id AS pid, pl.name, COALESCE(lx.level, 4) AS level FROM picks_xref AS px
          JOIN player pl
            ON px.player_id = pl.id
          JOIN pickset ps
            ON px.pickset_id = ps.id
          LEFT JOIN level_xref lx
            ON pl.id = lx.player_id AND ps.season_year = lx.season_year
          WHERE ps.id = %s ORDER BY lx.level
                      """
    def fill_picks(self, conn=None):
        conn = filter_conn(conn)

        results = conn.exec_fetch(Pickset.GET_PICKS_QUERY, (self.id,))

        self.picks = [player.Player(row['pid'], row['name'], level=row['level']) for row in results]

    def fill_tournament_history(self, year, conn=None):
        pass

    ### Overrides ###
    def __str__(self):
        s = "Pickset: id=%s, name='%s'" % (self.id, self.name)
        if self.pos is not None and self.points is not None:
            s += ", pos=%d, points=%d" % (self.pos, self.points)
        return s
