from collections import namedtuple
from typing import NamedTuple


class GlobalCache:
    live_tournament : NamedTuple = None

    @staticmethod
    def set_live_tournament(tid, year):
        LiveTournament = namedtuple("LiveTournament", ['tid' ,'year'])
        GlobalCache.live_tournament = LiveTournament(tid, year)
