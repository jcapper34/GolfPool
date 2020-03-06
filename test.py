from pprint import pprint
from picksets.picksets_test import *
from players.players_test import *
from db.conn import Conn
from standings.standings_test import test_fill_db_rankings, test_fill_db_standings

if __name__ == '__main__':
    conn = Conn()
    # test_fill_picks(conn=conn)
    # test_most_picked(conn=conn)
    # test_get_levels(conn=conn)
    # test_all_picks(conn=conn)

    test_fill_db_rankings(conn=conn)
    test_fill_db_standings(conn=conn)