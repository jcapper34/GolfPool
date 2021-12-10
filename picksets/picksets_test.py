from picksets.pickset import Pickset
from players.players_helper import level_separate
from picksets.picksets_db import get_most_picked, get_all_picks
from db.conn import Conn
from db.db_helper import filter_conn

""" INDIVIDUAL """
def test_fill_picks(psid=1, name='Sarah Mathy', conn=None):
    pickset = Pickset(id=psid, name=name)
    pickset.fill_picks(conn=conn)
    print(pickset.picks)
    # for level in pickset.picks:
    #     print('\t', [p.__str__() for p in level])

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
    pickset = Pickset(
        name='John Capper',
        email='j.capper2@gmail.com',
        pin=5753
    )
    success = pickset.submit_picks([
        ['Rickie Fowler*32102', 'Rory McIlroy*28237', 'Tiger Woods*08793'],
        ['Adam Scott*24502', 'Bryson DeChambeau*47959', 'Henrik Stenson*21528'],
        ['Aaron Wise*49964', 'Abraham Ancer*45526'],
        ['Aaron Wise*4960', 'Abraham Ancer*4526']
        ]
    )
    print(success)


if __name__ == '__main__':
    test_fill_picks()