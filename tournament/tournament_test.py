from helper import splash
import requests


def test_fill_db_rankings(year=2019, tid='014', conn=None):
    standings = Tournament()
    standings.fill_db_rankings(year=year, tid=tid, conn=conn)
    splash(standings.players)

def test_fill_db_standings(year=2019, tid='014', conn=None):
    standings = Tournament()
    standings.fill_db_standings(year=year, tid=tid, conn=conn)
    splash(standings.picksets)

def test_api():
    r = requests.head("https://www.pgatour.com/competition/2019/masters-tournament/leaderboard.html")
    print(r.headers)

if __name__ == "__main__":
    test_api()