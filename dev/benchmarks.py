import os
import sys
from timeit import timeit

import requests

APP_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, APP_ROOT)

from picksets.pickset_getters import get_all_picks
from tournament.tournament_calculations import calculate_standings
from tournament.tournament_retriever import get_api_tournament

def time_standings_calculations(trials=5):
    tournament = get_api_tournament(19540)
    conn = Conn()
    
    all_picks = get_all_picks(2022, conn=conn)
    duration = timeit(lambda: calculate_standings(tournament.players, all_picks), number=trials)/trials
    print("T1", duration)


def time_http(trials=5):
    url_root = "http://golf-pool.herokuapp.com"
    requests.get(url_root)
    
    h = {
        "Cache-Control": "no-cache",
        "Pragma": "no-cache"
    }
    
    duration = timeit(lambda: requests.get(url_root, headers=h), number=trials)/trials
    print("Home", duration)
    
    duration = timeit(lambda: requests.get(url_root+'/results/live', headers=h), number=trials)/trials
    print("Live", duration)
    
    duration = timeit(lambda: requests.get(url_root+'/results/2021/cumulative', headers=h), number=trials)/trials
    print("Past", duration)

    duration = timeit(lambda: requests.get(url_root+'/picks/poolwide/2022', headers=h), number=trials)/trials
    print("Poolwide", duration)

if __name__ == '__main__':
    t = time_http(20)
