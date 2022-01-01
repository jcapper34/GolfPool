import os
import sys

APP_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, APP_ROOT)

### Start Test Script Here ###
from helper import splash
import requests
from tournament.tournament import Tournament



def test_fill_db_rankings(year=2019, tid='014', conn=None):
    standings = Tournament(year=year, tid=tid)
    standings.fill_db_rankings(conn=conn)
    splash(standings.players)


def test_fill_db_standings(year=2019, tid='014', conn=None):
    standings = Tournament(year=year, tid=tid)
    standings.fill_db_standings(conn=conn)
    splash(standings.picksets)


def test_api():
    r = requests.head(
        "https://www.pgatour.com/competition/2019/masters-tournament/leaderboard.html")
    print(r.headers)


if __name__ == "__main__":
    test_api()
