from db.conn import Conn
from db.db_helper import filter_conn
from helper import CURRENT_YEAR
from players import player
from typing import List

class Pickset:
    """ CONSTANTS """
    PICKS_ALLOWED = [3, 3, 2, 2]


    """ CONSTRUCTOR """
    def __init__(self, psid=None, name=None, email=None, pin=None, picks=None, points=None, pos=None):
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



    """ HELPERS """
    def get_pids(self):
        pass


    """ PICK SUBMISSION """
    def submit_picks(self, form_picks):
        # Get main levels
        self.picks = []  # List of lists of type Player
        for level in form_picks:
            level_players = []
            for p in level:  # Iterate through form inputted players
                player_data = p.split('*')
                level_players.append(player.Player(name=player_data[0], pid=player_data[1]))

            self.picks.append(level_players)

        if not self.validate_picks():   ## Make sure picks are valid
            return False

        return self.insert_picks()

    def validate_picks(self):
        if len(self.picks) != len(Pickset.PICKS_ALLOWED):  ## Check for correct number of levels
            return False

        for i in range(len(self.picks)):
            level_players = self.picks[i]
            if len(level_players) != Pickset.PICKS_ALLOWED[i]:
                return False
        return True

    # Parameters: name, email, pin
    # Returns: participant.id
    INSERT_PARTICIPANT_QUERY = """
        INSERT INTO participant (name, email, pin) VALUES (%s,%s,%s)
        ON CONFLICT(name, email) DO UPDATE SET name=EXCLUDED.name
        RETURNING id
    """

    # Parameters: participant_id, season_year
    # Returns: pickset.id
    INSERT_PICKSET_QUERY = """
        INSERT INTO pickset (participant_id, season_year) VALUES (%s,%s)
        RETURNING id
    """
    def insert_picks(self, year=CURRENT_YEAR):
        conn = Conn()   # Make connection

        """ Ensure that level 4 players are not in levels 1-3 """
        results = conn.exec_fetch("SELECT player_id FROM level_xref WHERE season_year=%s", (2020,))
        level_pids = [x[0] for x in results]
        if any([p.id in level_pids for p in self.picks[3]]):
            return False

        """ Insert participant if doesn't exist """
        results = conn.exec_fetch(Pickset.INSERT_PARTICIPANT_QUERY, (self.name, self.email, self.pin))
        partid = results[0][0]

        """ Insert pickset """
        results = conn.exec_fetch(Pickset.INSERT_PICKSET_QUERY, (partid, year))
        psid = results[0][0]

        """ Insert picks """
        query = "INSERT INTO picks_xref (player_id, pickset_id) VALUES"
        for level_players in self.picks:
            for picked_player in level_players:
                s = conn.cur.mogrify(" (%s, %s),", (picked_player.id, 5)).decode("utf-8")
                query = ''.join((query, s))

        conn.exec(query[:-1])    # DB picks insert

        conn.commit()   # Make sure to commit changes


    """ DB FILLS """
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
