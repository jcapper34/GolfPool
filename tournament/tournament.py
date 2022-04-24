from dataclasses import dataclass
from typing import List
import json

from pprint import pprint
from datetime import datetime
from db.db_helper import filter_conn
from helper.helpers import func_find, CURRENT_YEAR, request_json
from picksets.pickset import Pickset
from picksets.pickset_getters import get_all_picks
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

    """ MERGES """
    def merge_all_picks(self, all_picks):
        for pickset in self.picksets:
            ps2 = func_find(all_picks, lambda ps: ps.id == pickset.id)
            pickset.picks = ps2.picks
