from db.conn import Conn
from db.db_helper import filter_conn
from helper import CURRENT_YEAR
from mailer.postman import Postman
from players import player
from typing import List

from players.players_helper import level_separate


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

    """ PICK SUBMISSION """
    def submit_picks(self, form_picks, conn=None):
        conn = filter_conn(conn)
        # Get main levels
        self.picks = Pickset.extract_form_picks(form_picks)

        if not self.validate_picks():   # Make sure picks are valid
            return False

        psid = self.db_inserts(conn=conn)

        # Send Email
        postman = Postman((self.email,))
        postman.make_picks_message(self.name, self.pin, self.picks)
        postman.send_message()

        return psid

    def submit_change_picks(self, form_picks, conn=None):
        conn = filter_conn(conn)

        # Get main levels
        self.picks = Pickset.extract_form_picks(form_picks)

        if not self.validate_picks():   # Make sure picks are valid
            return False

        self.db_update_picks(conn=conn)

        # Send email
        postman = Postman((self.email,))
        postman.make_picks_message(self.name, self.pin, self.picks, update=True)
        postman.send_message()

        return True


    @staticmethod
    def extract_form_picks(form_picks):
        picks = []  # Set of lists of type Player
        for level in form_picks:
            level_players = []
            for p in level:  # Iterate through form inputted players
                player_data = p.split('*')
                level_players.append(player.Player(name=player_data[0], pid=player_data[1]))

            picks.append(level_players)

        return picks

    def validate_picks(self):
        if len(self.picks) != len(Pickset.PICKS_ALLOWED):  ## Check for correct number of levels
            return False

        for i in range(len(self.picks)):
            level_players = self.picks[i]
            if len(level_players) != Pickset.PICKS_ALLOWED[i]:
                return False
        return True

    """ 
    Parameters: name, email, pin
    Returns: participant.id
    """
    INSERT_PARTICIPANT_QUERY = """
        INSERT INTO participant (name, email, pin) VALUES (%s,%s,%s)
        ON CONFLICT(name, email) DO UPDATE SET name=EXCLUDED.name, pin=EXCLUDED.pin
        RETURNING id
    """
    """
    Parameters: participant_id, season_year
    Returns: pickset.id
    """
    INSERT_PICKSET_QUERY = """
        INSERT INTO pickset (participant_id, season_year) VALUES (%s,%s)
        RETURNING id
    """
    def db_inserts(self, year=CURRENT_YEAR, conn=None):
        conn = filter_conn(conn)   # Make connection

        """ Ensure that level 4 players are not in levels 1-3 """
        results = conn.exec_fetch("SELECT player_id FROM level_xref WHERE season_year=%s", (CURRENT_YEAR,))
        level_pids = [x[0] for x in results]
        if any([p.id in level_pids for p in self.picks[3]]):
            return False

        """ Insert participant if doesn't exist """
        results = conn.exec_fetch(Pickset.INSERT_PARTICIPANT_QUERY, (self.name, self.email, self.pin))
        partid = results[0][0]

        """ Insert pickset """
        results = conn.exec_fetch(Pickset.INSERT_PICKSET_QUERY, (partid, year))
        self.id = results[0][0]

        """ Insert picks """
        self.db_insert_picks(conn=conn)

        conn.commit()   # Make sure to commit changes

        return self.id

    def db_insert_picks(self, conn=None):
        conn = filter_conn(conn)

        query = "INSERT INTO picks_xref (player_id, pickset_id) VALUES"
        for level_players in self.picks:
            for picked_player in level_players:
                # Create new db player if doesn't exist
                conn.exec("INSERT INTO player (id, name) VALUES (%s, %s) ON CONFLICT DO NOTHING", (picked_player.id, picked_player.name))

                # Add to picks insert query
                s = conn.cur.mogrify(" (%s, %s),", (picked_player.id, self.id)).decode("utf-8")
                query = ''.join((query, s))

        conn.exec(query[:-1])  # DB picks insert

    def db_update_picks(self, conn=None):
        conn = filter_conn(conn)

        conn.exec("DELETE FROM picks_xref WHERE pickset_id=%s", (self.id,))   # Delete previous picks

        self.db_insert_picks(conn=conn)  # Insert new picks

        conn.commit()


    """ DB FILLS """
    """
    Parameters: ps.id
    Returns: pid, pl.name, level, psname, pa.email, pa.pin
    """
    GET_PICKS_QUERY = """
    SELECT pl.id AS pid, pl.name, COALESCE(lx.level, 4) AS level, (pa.name || COALESCE(' - ' || ps.num, '')) AS psname, pa.email, pa.pin FROM picks_xref AS px
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
    def fill_picks(self, conn=None):
        conn = filter_conn(conn)

        results = conn.exec_fetch(Pickset.GET_PICKS_QUERY, (self.id,))
        if not results:
            return []

        self.picks = [player.Player(row['pid'], row['name'], level=row['level']) for row in results]
        self.picks = level_separate(self.picks)

        self.name = results[0]['psname']
        self.email = results[0]['email']
        self.pin = results[0]['pin']

    def fill_tournament_history(self, year, conn=None):
        pass


    """ HELPERS """
    def get_pids(self):
        return [p.id for level_players in self.picks for p in level_players]


    """ Overrides """
    def __str__(self):
        s = "Pickset: id=%s, name='%s'" % (self.id, self.name)
        if self.pos is not None and self.points is not None:
            s += ", pos=%d, points=%d" % (self.pos, self.points)
        return s
