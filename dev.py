from pprint import pprint

import requests

from db.db_helper import filter_conn
from helper import CURRENT_YEAR, func_find, splash, get_json
from db.conn import Conn
from tournament.tournament import Tournament


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


def db_upload_leaderboard_individual(tournament, conn=None):
    conn = filter_conn(conn)

    tournament.fill_api_leaderboard(live=False)

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

    conn.commit()

    print("Inserted leaderboard: %s - %d" % (tournament.name, tournament.year))

def db_upload_leaderboard(year, conn=None):
    conn = filter_conn(conn)

    api_events = get_json("https://www.golfchannel.com/api/v2/tours/1/events/%d" % year)
    major_results = [Tournament(year=year, channel_tid=e['key'], tournament_name=e['name']) for e in func_find(api_events, lambda event: event['major'], limit=4)]

    for major in major_results:
        lower_name = major.name.lower()
        if 'masters' in lower_name:
            major.tid = '014'
        elif 'us' or 'u.s.' in lower_name:
            major.tid = '026'
        elif 'open' in lower_name:
            major.tid = '100'
        elif 'championship' in lower_name:
            major.tid = '033'

        db_upload_leaderboard_individual(major, conn=conn)


if __name__ == "__main__":
    con = Conn()
    y = 2015
    for channel_tid, tid in [(16468, '026'),(16615, '100'),(16428, '033'), (16380, '014')]:
        db_upload_leaderboard_individual(Tournament(year=y, channel_tid=channel_tid, tid=tid), conn=con)

