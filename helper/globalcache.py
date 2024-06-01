from collections import namedtuple
from typing import NamedTuple


class GlobalCache:
    live_tournament : NamedTuple = None

    @staticmethod
    def set_live_tournament(name, tid, year):
        LiveTournament = namedtuple("LiveTournament", ['name', 'tid' ,'year'])
        GlobalCache.live_tournament = LiveTournament(name, tid, year)
        print("Set", GlobalCache.live_tournament)
