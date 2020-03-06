from helper import splash

from standings.standings import Standings


def test_fill_db_rankings(year=2019, tid='014', conn=None):
    standings = Standings()
    standings.fill_db_rankings(year=year, tid=tid, conn=conn)
    splash(standings.players)

def test_fill_db_standings(year=2019, tid='014', conn=None):
    standings = Standings()
    standings.fill_db_standings(year=year, tid=tid, conn=conn)
    splash(standings.picksets)