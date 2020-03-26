from pprint import pprint

import requests

from db.db_helper import filter_conn
from helper import CURRENT_YEAR, func_find, splash
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


def db_upload_leaderboard(year, tid, channel_tid, conn=None):
    conn = filter_conn(conn)

    tournament = Tournament(year=year, channel_tid=channel_tid, tid=tid)
    tournament.fill_api_leaderboard(live=False)


    splash(tournament.players)

    player_names = [pl['name'] for pl in conn.exec_fetch("SELECT * FROM player")]
    print(len(player_names))

    leaderboard_insert_query = "INSERT INTO event_leaderboard_xref (tournament_id, season_year, position, score, points, player_id) VALUES "

    print("Updating missing channel_ids")
    for player in tournament.players:
        # if player.name in player_names:
        #     conn.exec("UPDATE player SET id = %s WHERE name=%s", (player.id, player.name))
        values_query = conn.cur.mogrify(" (%s,%s,%s,%s,%s,%s,%s),", (tid, year, player.pos, player.total, player.points, player.id))
        leaderboard_insert_query += values_query.decode()

    print("Inserting leaderboard: %s - %d" % (tournament.name, tournament.year))
    conn.exec(leaderboard_insert_query[:-1])

    conn.commit()

if __name__ == "__main__":
    con = Conn()
    db_upload_leaderboard(year=2015, channel_tid=16380, tid="014", conn=con)