import json
from db.conn import Conn
from db.db_helper import filter_conn
from helper import func_find, CURRENT_YEAR
from picksets import pickset

from typing import List, ClassVar
from dataclasses import dataclass, asdict


@dataclass
class Player:
    # General
    id: str
    name: str
    tour_id: int = None
    level: int = None

    # Tournament
    points: int = None
    total: str = None
    pos: str = None
    raw_pos: int = None
    thru: str = None
    holes: list = None
    current_tournament_data: dict = None
    season_history: dict = None

    # Picks
    picked_by: List[str] = None
    num_picked: int = None

    # Photo
    photo_url: str = None
    country_flag: str = None

    # URL CONSTANTS #
    # From PGA Tour Website
    PGA_PHOTO_URL: ClassVar[str] = "https://pga-tour-res.cloudinary.com/image/upload/c_fill,d_headshots_default.png,dpr_2.0,f_auto,g_face:center,h_300,q_auto,w_300/headshots_%s.png"
    # OWGR_URL: ClassVar[str] = "https://statdata.pgatour.com/r/stats/%s/186.json"   # Takes year as argument
    ALL_PLAYERS_URL: ClassVar[str] = "https://statdata.pgatour.com/players/player.json"

    # From Golf Channel Website
    STAT_CATEGORIES_URL: ClassVar[str] = "https://www.golfchannel.com/api/v2/tours/1/stats/categories"
    OWGR_STAT_ID: ClassVar[int] = 19   # For OWGR ranking
    STATS_URL: ClassVar[str] = "https://www.golfchannel.com/api/v2/tours/1/stats/%d/2021"   # Parameters: Stat Number
    GOLFERS_URL: ClassVar[str] = "https://www.golfchannel.com/api/es/fullObject"

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

        self.picked_by = [pickset.Pickset(id=row['psid'], name=row['name']) for row in results]

        self.num_picked = len(self.picked_by)

    # Parameters: pid, year
    # Returns: pos, score, points, tid, thru, photo_url
    GET_TOURNAMENT_DATA_QUERY = """
    SELECT position AS pos, score AS total, points, tournament_id AS tid, 18 AS thru, p.photo_url FROM event_leaderboard_xref AS elx
        JOIN player p on elx.player_id = p.id
        WHERE p.id = %s AND elx.season_year=%s
    """
    def fill_tournament_data(self, tid, year, conn=None):
        conn = filter_conn(conn)

        self.tournament_data = conn.exec_fetch(Player.GET_TOURNAMENT_DATA_QUERY, (self.id, year))
        self.tournament_data = list(self.tournament_data)

        self.current_tournament_data = func_find(self.tournament_data, lambda t: t['tid'] == tid)
        self.photo_url = self.tournament_data[0]['photo_url']

    def merge(self, player):
        for key, val in vars(self).items():
            if val is None and getattr(player, key) is not None:
                setattr(self, key, getattr(player, key))

    """ Overrides """
    def __str__(self):
        return "Player: id=%s, name='%s'" % (self.id, self.name)

    def __hash__(self):         # So 'in' keyword can be used
        return int(self.id)

    def __eq__(self, other):    # Allows for comparison
        return self.id == other.id and self.name == other.name
    
    def __dict__(self):
        return asdict(self)


if __name__ == '__main__':
    pl = Player(id="874", name="he")
    print(json.dump(asdict(pl)))
