from dataclasses import asdict, dataclass
from helper.helpers import func_find
from typing import List, ClassVar

from players.player import Player



@dataclass
class Pickset:
    # General Info
    id: int = None
    name: str = None
    email: str = None
    pin: str = None

    # Picks
    picks: List[Player] = None

    # Tournament Info
    points: int = None
    pos: int = None
    tournament_history: List = None

    def get_pids(self) -> List:
        return [p.id for level_players in self.picks for p in level_players]

    def merge_tournament(self, tournament) -> None:
        for golfer in self.picks:
            pl = func_find(tournament.players, lambda p: p.id == golfer.id)
            if pl is None:  # If not found
                golfer.points = 0
                continue
            
            golfer.pos = pl.pos
            golfer.total = pl.total
            golfer.points = pl.points
            golfer.thru = pl.thru
            golfer.status = pl.status

    def __str__(self) -> str:
        s = "Pickset: id=%s, name='%s'" % (self.id, self.name)
        if self.pos is not None and self.points is not None:
            s += ", pos=%d, points=%d" % (self.pos, self.points)
        return s

    def __dict__(self) -> None:
        return asdict(self)
