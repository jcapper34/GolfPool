from pprint import pprint
from datetime import datetime
from db.db_helper import filter_conn
from helper import func_find, CURRENT_YEAR, get_json, NOW
from picksets.pickset import Pickset
from picksets.picksets_db import get_all_picks
from players.player import Player


class Tournament:
    # Golf Channel URL
    LEADERBOARD_URL = "https://www.golfchannel.com/api/v2/events/%d/leaderboard" # Parameters: int[tournament_id]
    EVENTS_URL = "https://www.golfchannel.com/api/v2/tours/1/events/%d" # Parameters: int[year]

    def __init__(self, tid=None, year=CURRENT_YEAR, tournament_name=None, channel_tid=None):
        self.tid = tid
        self.year = year
        self.name = tournament_name
        self.channel_tid = channel_tid

        self.players = []
        self.picksets = []

    # TODO: DB Leaderboard is wack
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
    def fill_db_rankings(self, conn=None):
        conn = filter_conn(conn)

        raw_players = conn.exec_fetch(Tournament.GET_DB_RANKINGS_QUERY, (self.year, self.tid if self.tid != 'cumulative' else None))

        if not raw_players:
            return False

        self.players = [Player(**p) for p in raw_players]

        # Associate tournament names
        tournament_names = {
            "014": "The Masters",
            "026": "U.S Open",
            "100": "British Open",
            "033": "PGA Championship",
            'cumulative': 'Cumulative'
        }

        self.name = tournament_names[self.tid]

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
    def fill_db_standings(self, conn=None):
        conn = filter_conn(conn)

        results = conn.exec_fetch(Tournament.GET_DB_STANDINGS_QUERY, (self.year, self.tid if self.tid != 'cumulative' else None))
        if not results:
            return False

        self.picksets = [Pickset(psid=row['psid'], name=row['name'], points=row['points'], pos=row['pos']) for row in results]

        return True

    """ API FILLS """
    @staticmethod
    def api_get_live():
        # events = get_json(Tournament.EVENTS_URL % CURRENT_YEAR)
        # current_tournament = func_find(events, lambda e: NOW < datetime.strptime(e['endDate'], "%Y-%m-%dT%H:%M:%S"))    # Finds first event with end date after now
        return get_json(Tournament.LEADERBOARD_URL % 18491)


    def fill_api_leaderboard(self):
        if self.channel_tid is None: # If live is requested
            api_tournament = self.api_get_live()['result'] # Get Tournament From API
        else:
            api_tournament = get_json(Tournament.LEADERBOARD_URL % self.channel_tid)['result'] # Get Tournament From API

        try:
            point_template = get_json('tournament/data/point-template.json')  # Load Point Template Data
        except FileNotFoundError:
            point_template = get_json('../tournament/data/point-template.json')  # Load Point Template Data

        leaderboard = api_tournament['golfers']
        self.channel_tid = api_tournament.get('eventKey')
        self.players = [Player(pid=pl['golferId'],
                               name=pl['firstName'] + " " + pl['lastName'],
                               pos=pl['position'],
                               points=point_template[str(pl['sortHelp'])] if pl['sortHelp'] is not None and pl['sortHelp'] <= 20 else 0,
                               raw_pos=pl['sortHelp'],
                               total=pl['overallPar'],
                               thru=pl['thruHole'],
                               photo_url=pl['imageUrl']
                               ) for pl in leaderboard] # Create Player objects of leaderboard
        self.players.sort(key=lambda x: (x.raw_pos is None, x.raw_pos))     # Sort so that None is at the end
        self.name = api_tournament.get("eventName")


    """ CALCULATIONS """
    def calculate_api_standings(self, get_picks=True, conn=None):
        conn = filter_conn(conn)

        if get_picks:
            self.picksets = get_all_picks(self.year, conn=conn) # Load DB Picks

        for pickset in self.picksets:
            if pickset.points is None:
                pickset.points = 0
            for picked_player in pickset.picks:
                match = func_find(self.players, func=lambda x: x.id == picked_player.id)
                if match is not None:
                    pickset.points += match.points
                    picked_player.merge(match)

        self.picksets.sort(key=lambda x: x.points, reverse=True)    # Sort Standings
        self.rank()

    def rank(self): # Give Picksets their positions after calculating standings
        n = len(self.picksets)
        pos = 1
        for i in range(n):
            points = self.picksets[i].points
            tie = False
            if i == 0 and n > 1 and points == self.picksets[i + 1].points:
                tie = True
            elif points == self.picksets[i - 1].points:
                tie = True
            if not tie:
                pos = i + 1

            self.picksets[i].pos = pos

    @staticmethod
    def get_passed_events(conn=None): # Used to get all season years that have been stored in DB
        conn = filter_conn(conn)
        results = conn.exec_fetch("""
        SELECT season_year, tournament.id, tournament.name from event 
            JOIN tournament ON event.tournament_id = tournament.id
            ORDER BY season_year DESC
        """)

        year_tourny = {}
        for row in results:
            info = {
                    'id': row[1],
                    'name': row[2]
                }
            if year_tourny.get(row[0]) is None:
                year_tourny[row[0]] = [info]
            else:
                year_tourny[row[0]].append(info)

        return year_tourny

    """ MERGES """
    def merge_all_picks(self, all_picks):
        for pickset in self.picksets:
            ps2 = func_find(all_picks, lambda ps: ps.id == pickset.id)
            pickset.picks = ps2.picks