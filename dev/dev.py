from pprint import pprint

import requests
from config import ALL_PLAYERS_URL, OWGR_STAT_ID, PGA_PHOTO_URL, STATS_URL

from db.db_helper import filter_conn
from helper.helpers import CURRENT_YEAR, func_find, splash, request_json
from db.conn import Conn
from picksets.pickset_getters import get_all_picks
from players.player import Player
from tournament.tournament_calculations import calculate_api_standings, calculate_standings
from tournament.tournament import Tournament
from tournament.tournament_retriever import get_api_tournament

"""
Channel TIDS
- 2019 Masters: 17893
- 2019 US Open: 17902

- 2017 Masters: 16936  
- 2017 US Open: 16946  
- 2017 The Open: 16953    
- 2017 PGA Championship: 16957

- 2016 US Open: 16610
- 2016 Masters: 16639
- 2016 The Open: 16615
- 2016 PGA Championship: 16618
"""


def get_email_addresses(year):
    conn = Conn()
    results = conn.exec_fetch("""
        SELECT DISTINCT pa.email FROM participant AS pa
        JOIN pickset ON pa.id = pickset.participant_id
        WHERE season_year = %s
        """, (year, ))

    return '; '.join([email for a in results for email in a])


def insert_levels(year=CURRENT_YEAR):
    levels = (
        (
            'Rory McIlroy',
            'Jon Rahm',
            'Brooks Koepka',
            'Justin Thomas',
            'Dustin Johnson',
            'Bryson DeChambeau',
            'Patrick Reed',
            'Patrick Cantlay',
            'Webb Simpson',
            'Collin Morikawa',
            'Xander Schauffele',
            'Tyrrell Hatton',
            'Tony Finau'
        ),
        (
            'Sungjae Im',
            'Viktor Hovland',
            'Daniel Berger',
            'Matthew Fitzpatrick',
            'Billy Horschel',
            'Paul Casey',
            'Lee Westwood',
            'Harris English',
            'Scottie Scheffler',
            'Matthew Wolff',
            'Tommy Fleetwood',
            'Hideki Matsuyama',
            'Ryan Palmer',
            'Louis Oosthuizen',
            'Adam Scott',
            'Justin Rose',

        ),
        (
            'Kevin Na',
            'Abraham Ancer',
            'Joaquin Niemann',
            'Victor Perez',
            'Cameron Smith',
            'Jason Kokrak',
            'Christiaan Bezuidenhout',
            'Kevin Kisner',
            'Max Homa',
            'Marc Leishman',
            'Sergio Garcia',
            'Corey Conners',
            'Henrik Stenson',
            'Matt Kuchar',
            'Jason Day',
            'Shane Lowry',
            'Jordan Spieth',
            'Gary Woodland',
            'Bubba Watson',
            'Bernd Wiesberger',
            'Phil Mickelson',
            'Rickie Fowler',
            'Danny Willett',
            'Ian Poulter',
            'Si Woo Kim'

        )
    )
    for level in levels:
        for player in sorted(level):
            print(player)
        print()
    check_levels_good(levels)

    conn = Conn()

    # Do clean up
    conn.exec("DELETE FROM level_xref WHERE season_year = %s", (year,))

    for level_num in range(1, len(levels)+1):
        for player_name in levels[level_num-1]:
            results = conn.exec_fetch(
                "SELECT id FROM player WHERE name=%s", (player_name,), fetchall=False)    # Get player id
            if results is None:
                print("Player %s does not exist" % player_name)
                continue
            pid = results[0]
            conn.exec(
                "INSERT INTO level_xref (player_id, season_year, level) VALUES(%s,%s,%s)", (pid, year, level_num))

    conn.commit()


def db_set_photo_urls(conn=None):
    conn = filter_conn(conn)
    db_players = conn.exec_fetch(
        "SELECT id, name FROM player WHERE tour_id is NULL")
    api_players = request_json(ALL_PLAYERS_URL)['plrs']

    for player in db_players:
        match = func_find(api_players, lambda pl: ' '.join(
            (pl['nameF'], pl['nameL'])).lower() == player['name'].lower())
        if match is not None:
            pid = match['pid']
            conn.exec("UPDATE player SET tour_id = %s, photo_url = %s WHERE id=%s",
                      (pid, PGA_PHOTO_URL % pid, player['id']))

    conn.commit()


def check_levels_good(levels):
    # flattened_levels = [pl for level in levels for pl in level]
    owgr_data = requests.get(STATS_URL %
                             OWGR_STAT_ID).json()[:100]
    for i, player in enumerate(owgr_data, start=1):
        p_name = player['firstName'] + " " + player['lastName']
        found = False
        for level in levels:
            if func_find(level, lambda pl: p_name == pl):
                print(i, p_name, levels.index(level)+1, sep='\t\t')
                found = True

        if not found:
            print(i, p_name, "X", sep='\t\t')


if __name__ == "__main__":
    insert_levels(CURRENT_YEAR)
    # con = Conn()
    # for channel_tid, tid in []:
    #     tournament = Tournament(channel_tid=channel_tid, tid=tid, year=2021)
    #     db_upload_standings_individual(tournament, conn=con)
    #     db_upload_leaderboard_individual(channel_tid, tid, 2021, conn=con)
