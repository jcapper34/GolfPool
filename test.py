from pprint import pprint

from mailer.test_mailer import test_picks_send
from picksets.picksets_test import *
from players.players_test import *
from db.conn import Conn
from tournament.tournament import Tournament
from tournament.tournament_test import test_fill_db_rankings, test_fill_db_standings
from mailer.postman import Postman

if __name__ == '__main__':
    # conn = Conn()
    # # test_fill_picks(conn=conn)
    # # test_most_picked(conn=conn)
    # # test_get_levels(conn=conn)
    # # test_all_picks(conn=conn)
    #
    # test_fill_db_rankings(conn=conn)
    # test_fill_db_standings(conn=conn)
    tournament = Tournament(year=2019)
    tournament.api_get_live()