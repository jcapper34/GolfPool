import os
import sys

APP_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, APP_ROOT)

### Start Test Script Here ###
from pprint import pprint
from helper.helpers import func_find, splash
from test.mailer_test import test_picks_send
from db.conn import Conn
from tournament.tournament import Tournament
from test.tournament_test import test_fill_db_rankings, test_fill_db_standings
from mailer.postman import Postman

from players.player_getters import *
from players.player import Player
from picksets.pickset_submission import *
from picksets.pickset_getters import *
from db.conn import Conn
from db.db_helper import filter_conn


def test_get_levels(year=2019, conn=None):
    levels = get_levels_db(year, conn=conn)
    print("LEVELS FOR %d" % year)
    for level in levels:
        print('\t', [pl.__str__() for pl in level])


def test_get_picks(psid=1, conn=None):
    picks = get_picks(psid, conn=conn)
    for level in picks:
        print('\t', [str(p) for p in level])


def test_most_picked(year=2019, conn=None):
    most_picked = get_most_picked(year, conn=conn)
    print("MOST PICKED PLAYERS FOR %d" % year)
    for player in most_picked:
        print('\t', player.__str__(), player.num_picked)


def test_all_picks(year=2019, conn=None):
    all_picks = get_all_picks(year, conn)
    picks_len = len(all_picks[0].picks)
    for pickset in all_picks:
        if len(pickset.picks) != picks_len:
            print("Unequal number of picksets")


def test_submit_picks():
    name = 'John Capper',
    email = 'j.capper2@gmail.com',
    pin = 5753
    form_picks = [
        ('Rickie Fowler*32102', 'Rory McIlroy*28237', 'Tiger Woods*08793'),
        ('Adam Scott*24502', 'Bryson DeChambeau*47959', 'Henrik Stenson*21528'),
        ('Aaron Wise*49964', 'Abraham Ancer*45526'),
        ('Aaron Wise*4960', 'Abraham Ancer*4526')
    ]
    return submit_picks(name, email, pin, form_picks, send_email=False, year=2022)


if __name__ == '__main__':
    # psid = test_submit_picks()
    test_get_picks()
