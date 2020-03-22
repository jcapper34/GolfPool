from helper import splash

from tournament.tournament import Tournament


def test_fill_db_rankings(year=2019, tid='014', conn=None):
    standings = Tournament()
    standings.fill_db_rankings(year=year, tid=tid, conn=conn)
    splash(standings.players)

def test_fill_db_standings(year=2019, tid='014', conn=None):
    standings = Tournament()
    standings.fill_db_standings(year=year, tid=tid, conn=conn)
    splash(standings.picksets)