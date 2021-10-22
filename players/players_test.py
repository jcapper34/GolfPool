from players.players_db import *
from players.player import Player
from db.conn import Conn
from db.db_helper import filter_conn

def test_get_levels(year=2019, conn=None):
    levels = get_levels(year, conn=conn)
    print("LEVELS FOR %d" % year)
    for level in levels:
        print('\t', [pl.__str__() for pl in level])





