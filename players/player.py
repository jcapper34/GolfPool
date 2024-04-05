
from typing import Any, List
from dataclasses import dataclass, asdict


@dataclass
class Player:
    # General
    id: str
    name: str = None
    level: int = None

    # Tournament
    points: int = None
    total: str = None
    pos: str = None
    raw_pos: int = None
    thru: str = None
    status: str = ""
    holes: list = None
    season_history: dict = None
    scorecards: List = None

    # Picks
    picked_by: List[str] = None
    num_picked: int = None

    # Photo
    photo_url: str = None
    country_flag: str = None

    def set_attributes(self, attr_map) -> None:
        for key, val in attr_map.items():
            setattr(self, key, val)
            
    def merge_attributes(self, attr_map) -> None:
        for key, val in attr_map.items():
            if getattr(self, key) is None:
                setattr(self, key, val)

    """ Overrides """
    def __str__(self) -> str:
        return "Player: [id=%s, name='%s']" % (self.id, self.name)

    def __hash__(self) -> Any:         # So 'in' keyword can be used
        return int(self.id)

    def __eq__(self, other) -> bool:    # Allows for comparison
        return self.id == other.id and self.name == other.name

    def __dict__(self) -> dict:
        return asdict(self)
