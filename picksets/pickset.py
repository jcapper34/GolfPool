from dataclasses import asdict, dataclass
from db.conn import Conn
from db.db_helper import filter_conn
from helper import CURRENT_YEAR, func_find
from mailer.postman import Postman
from players import player
from typing import List, ClassVar

from players.players_helper import level_separate


@dataclass
class Pickset:
    # General Info
    id: int = None
    name: str = None
    email: str = None
    pin: str = None

    # Picks
    picks: List = None

    # Tournament Info
    points: int = None
    pos: int = None
    tournament_history: List = None

    """ CONSTANTS """
    PICKS_ALLOWED: ClassVar[List[int]] = [3, 3, 2, 2]

    # """
    # Parameters: season_year, ps.id
    # Returns: tournament.name, pos, points
    # """
    # GET_TOURNAMENT_HISTORY_QUERY = """SELECT t.name, esx.position AS pos, esx.points FROM event_standings_xref AS esx
    #                                                     JOIN tournament AS t
    #                                                         ON t.id = esx.tournament_id
    #                                                     WHERE esx.season_year = %s AND esx.pickset_id = %s"""

    # def fill_tournament_history(self, year, conn=None):
    #     conn = filter_conn(conn)

    #     self.tournament_history = conn.exec_fetch(
    #         Pickset.GET_TOURNAMENT_HISTORY_QUERY, (year, self.id))

    def get_pids(self):
        return [p.id for level_players in self.picks for p in level_players]

    def merge_tournament(self, tournament):
        for golfer in self.picks:
            pl = func_find(tournament.players, lambda p: p.id == golfer.id)
            if pl is None:  # If not found
                golfer.points = 0
                continue

            golfer.merge(pl)

    """ Overrides """

    def __str__(self):
        s = "Pickset: id=%s, name='%s'" % (self.id, self.name)
        if self.pos is not None and self.points is not None:
            s += ", pos=%d, points=%d" % (self.pos, self.points)
        return s

    def __dict__(self):
        return asdict(self)
