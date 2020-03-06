from db.conn import Conn
from db.db_helper import filter_conn
from picksets import pickset

class Player:
    def __init__(self, pid, name=None, **kwargs):
        # General
        self.id = pid
        self.name = name
        self.level = kwargs.get("level")

        # Tournament
        self.points = kwargs.get("points")
        self.total = kwargs.get("total")
        self.pos = kwargs.get("pos")
        self.thru = kwargs.get("thru")
        self.holes = kwargs.get("holes")

        # Picks
        self.picked_by = None
        self.num_picked = kwargs.get("num_picked")


    # Parameters: pid, year
    # Returns: psid, name
    GET_WHO_PICKED_QUERY = """SELECT ps.id AS psid, (pa.name || COALESCE(' - ' || ps.num, '')) AS name FROM pickset AS ps
                        JOIN picks_xref px on ps.id = px.pickset_id
                        JOIN participant pa on ps.participant_id = pa.id
                        WHERE px.player_id = %s AND ps.season_year = %s
                        ORDER BY name"""

    def fill_who_picked(self, year, conn=None):
        conn = filter_conn(conn)

        results = conn.exec_fetch(self.GET_WHO_PICKED_QUERY, (self.id, year))

        self.picked_by = [pickset.Pickset(psid=row['psid'], name=row['name']) for row in results]


    def fill_tournament_data(self, tid, year):
        pass

    def fill_tournament_history(self, year, conn=None):
        pass



    ### Overrides ###
    def __str__(self):
        return "Player: id=%s, name='%s'" % (self.id, self.name)