from dataclasses import dataclass
from typing import List

from helper.helpers import CURRENT_YEAR, func_find
from picksets.pickset import Pickset
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
