from pprint import pprint

import requests

from db.db_helper import filter_conn
from helper import CURRENT_YEAR, func_find, splash, get_json
from db.conn import Conn
from tournament.tournament import Tournament

"""
Channel TIDS
- 2019 Masters: 17893
- 2019 US Open: 17902
"""



def insert_levels(year=CURRENT_YEAR):
    levels = (
        (
         'Rory McIlroy',
         'Jon Rahm',
         'Brooks Koepka',
         'Justin Thomas',
         'Dustin Johnson',
         'Adam Scott',
         'Patrick Reed',
         'Patrick Cantlay',
         'Webb Simpson',
         'Tommy Fleetwood',
         'Tiger Woods',
         'Justin Rose'
        ),
        (
        'Xander Schauffele',
        'Bryson DeChambeau',
        'Marc Leishman',
        'Tony Finau',
        'Matt Kuchar',
        'Gary Woodland',
        'Louis Oosthuizen',
        'Shane Lowry',
        'Tyrrell Hatton',
        'Hideki Matsuyama',
        'Paul Casey',
        'Matthew Fitzpatrick',
        'Rickie Fowler',
        'Henrik Stenson',
        'Sergio Garcia',
        'Jordan Spieth',
        'Jason Day',
        'Bubba Watson'
        ),
        (
        'Sungjae Im',
        'Bernd Wiesberger',
        'Francesco Molinari',
        'Abraham Ancer',
        'Kevin Na',
        'Lee Westwood',
        'Danny Willett',
        'Billy Horschel',
        'Cameron Smith',
        'Kevin Kisner',
        'Chez Reavie',
        'Rafa Cabrera Bello',
        'Jazz Janewattananond',
        'Scottie Scheffler',
        'Brandt Snedeker',
        'Graeme McDowell',
        'Ian Poulter',
        'Phil Mickelson',
        'Keegan Bradley',
        'Branden Grace',
        'Adam Hadwin',
        )
    )
    conn = Conn()

    # Do clean up
    conn.exec("DELETE FROM level_xref WHERE season_year = %s", (year,))

    for level_num in range(1, len(levels)+1):
        for player_name in levels[level_num-1]:
            results = conn.exec_fetch("SELECT id FROM player WHERE name=%s", (player_name,), fetchall=False)    # Get player id
            if results is None:
                print("Player %s does not exist" % player_name)
                continue
            pid = results[0]
            conn.exec("INSERT INTO level_xref (player_id, season_year, level) VALUES(%s,%s,%s)", (pid, year, level_num))

    conn.commit()


def db_upload_leaderboard_individual(tournament, do_commit=True, conn=None):
    conn = filter_conn(conn)

    tournament.fill_api_leaderboard()

    conn.exec('INSERT INTO season VALUES (%s) ON CONFLICT DO NOTHING', (tournament.year,))  # Insert season

    conn.exec("DELETE FROM event_leaderboard_xref CASCADE WHERE tournament_id=%s AND season_year=%s", (tournament.tid, tournament.year))
    conn.exec('INSERT INTO event (tournament_id, season_year) VALUES (%s, %s) ON CONFLICT DO NOTHING',
              (tournament.tid, tournament.year))  # Insert season

    leaderboard_insert_query = "INSERT INTO event_leaderboard_xref (tournament_id, season_year, position, score, points, player_id) VALUES "

    for player in tournament.players:
        conn.exec("INSERT INTO player (id, name) VALUES (%s,%s) ON CONFLICT DO NOTHING", (player.id, player.name))
        values_query = conn.cur.mogrify(" (%s,%s,%s,%s,%s,%s),",
                                        (tournament.tid, tournament.year, player.pos, player.total, player.points, player.id))
        leaderboard_insert_query += values_query.decode()

    conn.exec(leaderboard_insert_query[:-1] + " ON CONFLICT DO NOTHING")

    if do_commit:
        conn.commit()

    print("Inserted leaderboard: %s - %d" % (tournament.name, tournament.year))

def db_upload_leaderboard(year, conn=None):
    conn = filter_conn(conn)

    for i in range(1, 4):
        api_events = get_json("https://www.golfchannel.com/api/v2/tours/%d/events/%d" % (i,year))
        try:
            major_results = [Tournament(year=year, channel_tid=e['key'], tournament_name=e['name'])
                         for e in func_find(api_events, lambda event: event['major'] and 'players' not in event['name'], limit=4)]
        except TypeError:
            print("NONE")
        print([m.name for m in major_results])
    return

    assert len(major_results) == 4
    assert all(['players' not in m.name.lower() for m in major_results])

    for major in major_results:
        lower_name = major.name.lower()
        if 'masters' in lower_name:
            major.tid = '014'
        elif 'us open' in lower_name or 'u.s. open' in lower_name:
            major.tid = '026'
        elif 'the open' in lower_name:
            major.tid = '100'
        elif 'championship' in lower_name:
            major.tid = '033'
        else:
            raise AttributeError("Can't find tid for %s" % major.name)

        db_upload_leaderboard_individual(major, do_commit=False, conn=conn)

    conn.commit()

if __name__ == "__main__":
    con = Conn()
    # y = 2015
    # for channel_tid, tid in [(16468, '026'),(16615, '100'),(16428, '033'), (16380, '014')]:
    #     db_upload_leaderboard_individual(Tournament(year=y, channel_tid=channel_tid, tid=tid), conn=con)
    for y in range(2015, 2020):
        try:
            db_upload_leaderboard(y, conn=con)
        except AssertionError:
            print("Unable to get all majors for %d" % y)

