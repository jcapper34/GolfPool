from pprint import pprint

from helper import func_find, splash
from mailer.test_mailer import test_picks_send
from picksets.picksets_test import *
from players.players_test import *
from db.conn import Conn
from tournament.tournament import Tournament
from tournament.tournament_test import test_fill_db_rankings, test_fill_db_standings
from mailer.postman import Postman

def test_graph():
    conn = Conn()
    players_history = []
    for year in range(2016, 2020):
        tournament = Tournament(year=year, tid='cumulative')
        tournament.fill_db_rankings(conn=conn)
        player_data = func_find(tournament.players, lambda pl: pl.id == 11111)
        players_history.append(player_data.pos if player_data is not None else None)

    print(players_history)



if __name__ == '__main__':
    pass
    # conn = Conn()
    # results = conn.exec_fetch("SELECT season_year, tournament_id from event ORDER BY season_year DESC")
    #
    # year_tourny = {}
    # for row in results:
    #     tournament_id = row[1]
    #     if year_tourny.get(row[0]) is None:
    #         year_tourny[row[0]] = [tournament_id]
    #     else:
    #         year_tourny[row[0]].append(year_tourny[row[0]])
    #
    # print(year_tourny)

