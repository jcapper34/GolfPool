from db.conn import Conn
from db.db_helper import filter_conn
from helper import func_find, CURRENT_YEAR
from picksets import pickset


class Player:
    # From PGA Tour Website
    PGA_PHOTO_URL = "https://pga-tour-res.cloudinary.com/image/upload/c_fill,d_headshots_default.png,dpr_2.0,f_auto,g_face:center,h_300,q_auto,w_300/headshots_%s.png"
    # OWGR_URL = "https://statdata.pgatour.com/r/stats/%s/186.json"   # Takes year as argument
    # ALL_PLAYERS_URL = "https://statdata.pgatour.com/players/player.json"

    # From Golf Channel Website
    STAT_CATEGORIES_URL = "https://www.golfchannel.com/api/v2/tours/1/stats/categories"
    STATS_URL = "https://www.golfchannel.com/api/v2/tours/1/stats/%d/2020"   # Parameters: Stat Number
    GOLFERS_URL = "https://www.golfchannel.com/api/search/objectGolferVerbose?full=true"

    def __init__(self, pid, name=None, **kwargs):
        # General
        self.id = pid
        self.name = name
        self.tour_id = kwargs.get("tour_id")
        self.level = kwargs.get("level")

        # Tournament
        self.points = kwargs.get("points")
        self.total = kwargs.get("total")
        self.pos = kwargs.get("pos")
        self.thru = kwargs.get("thru")
        self.holes = kwargs.get("holes")

        self.tournament_data = None
        self.current_tournament_data = None

        self.season_history = None

        # Picks
        self.picked_by = None
        self.num_picked = kwargs.get("num_picked")

        # Photo
        self.photo_url = Player.PGA_PHOTO_URL % self.tour_id if kwargs.get('photo_url') is None else kwargs.get('photo_url')


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

        self.num_picked = len(self.picked_by)

    # Parameters: pid, year
    # Returns: pos, score, points, tid, thru
    GET_TOURNAMENT_DATA_QUERY = """
    SELECT position AS pos, score AS total, points, tournament_id AS tid, 18 AS thru, player_tour_id AS tour_id FROM event_leaderboard_xref 
        WHERE player_id = %s AND season_year=%s
    """
    def fill_tournament_data(self, tid, year, conn=None):
        conn = filter_conn(conn)

        self.tournament_data = conn.exec_fetch(Player.GET_TOURNAMENT_DATA_QUERY, (self.id, year))
        self.tournament_data = list(self.tournament_data)

        self.current_tournament_data = func_find(self.tournament_data, lambda t: t['tid'] == tid)

    """ Overrides """
    def __str__(self):
        return "Player: id=%s, name='%s'" % (self.id, self.name)

    def __hash__(self): # So 'in' keyword can be used
        return int(self.id)

    def __eq__(self, other):    # Allows for comparison
        return self.id == other.id and self.name == other.name