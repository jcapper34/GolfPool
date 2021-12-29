import json
import logging
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
    name: str = None
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

    def merge(self, player):
        for prop in Player.__dataclass_fields__:
            val = getattr(self, prop)
            if val is None and getattr(player, prop) is not None:
                setattr(self, prop, getattr(player, prop))

    """ Overrides """
    def __str__(self):
        return "Player: [id=%s, name='%s']" % (self.id, self.name)

    def __hash__(self):         # So 'in' keyword can be used
        return int(self.id)

    def __eq__(self, other):    # Allows for comparison
        return self.id == other.id and self.name == other.name
    
    def __dict__(self):
        return asdict(self)
