from dataclasses import dataclass
from typing import List, ClassVar
import json

from pprint import pprint
from datetime import datetime
from db.db_helper import filter_conn
from helper import func_find, CURRENT_YEAR, request_json
from picksets.pickset import Pickset
from picksets.picksets_db import get_all_picks
from players.player import Player


@dataclass
class Tournament:
    tid: int = None
    year: int = CURRENT_YEAR
    name: str = None
    channel_tid: str = None

    players: List[Player] = None
    picksets: List[Pickset] = None
    scorecards: List = None

    ### DATABASE FILLS ###

    # Parameters: year, tid
    # Returns: pid, name, points, pos ORDERED BY points
    GET_DB_RANKINGS_QUERY = """
    WITH leaderboard AS (SELECT pl.id, pl.name, SUM(elx.points) as points, RANK() OVER(ORDER BY SUM(elx.points) DESC) AS pos FROM event_leaderboard_xref AS elx
      JOIN event
        ON event.tournament_id = elx.tournament_id AND event.season_year = elx.season_year
      JOIN tournament AS t
          ON t.id = event.tournament_id
      JOIN player AS pl
        ON pl.id = elx.player_id
      WHERE event.season_year = %s AND elx.tournament_id = COALESCE(%s, elx.tournament_id)
      GROUP BY pl.id, pl.name)
      SELECT * FROM leaderboard WHERE points > 0
                          """

    def fill_db_rankings(self, conn=None):
        conn = filter_conn(conn)

        raw_players = conn.exec_fetch(Tournament.GET_DB_RANKINGS_QUERY, (
            self.year, self.tid if self.tid != 'cumulative' else None))

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

        results = conn.exec_fetch(Tournament.GET_DB_STANDINGS_QUERY,
                                  (self.year, self.tid if self.tid != 'cumulative' else None))
        if not results:
            return False

        self.picksets = [Pickset(id=row['psid'], name=row['name'],
                                 points=row['points'], pos=row['pos']) for row in results]

        return True

    @staticmethod
    # Used to get all season years that have been stored in DB
    def get_past_events(conn=None):
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
