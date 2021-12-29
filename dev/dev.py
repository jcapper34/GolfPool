from pprint import pprint

import requests

from db.db_helper import filter_conn
from helper import CURRENT_YEAR, func_find, splash, request_json
from db.conn import Conn
from players.player import Player
from tournament.standings_calc import calculate_api_standings
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


def db_upload_leaderboard_individual(tournament, do_commit=True, conn=None):
    conn = filter_conn(conn)

    tournament.fill_api_leaderboard()

    conn.exec('INSERT INTO season VALUES (%s) ON CONFLICT DO NOTHING',
              (tournament.year,))  # Insert season

    conn.exec("DELETE FROM event_leaderboard_xref CASCADE WHERE tournament_id=%s AND season_year=%s",
              (tournament.tid, tournament.year))
    conn.exec('INSERT INTO event (tournament_id, season_year) VALUES (%s, %s) ON CONFLICT DO NOTHING',
              (tournament.tid, tournament.year))  # Insert season

    leaderboard_insert_query = "INSERT INTO event_leaderboard_xref (tournament_id, season_year, position, score, points, player_id) VALUES "

    for player in tournament.players:
        conn.exec("INSERT INTO player (id, name) VALUES (%s,%s) ON CONFLICT DO NOTHING",
                  (player.id, player.name))
        values_query = conn.cur.mogrify(" (%s,%s,%s,%s,%s,%s),",
                                        (tournament.tid, tournament.year, player.pos, player.total, player.points, player.id))
        leaderboard_insert_query += values_query.decode()

    conn.exec(leaderboard_insert_query[:-1] + " ON CONFLICT DO NOTHING")

    if do_commit:
        conn.commit()

    print("Inserted leaderboard: %s - %d" % (tournament.name, tournament.year))


def db_upload_leaderboard(year, conn=None):
    conn = filter_conn(conn)

    api_events = request_json(
        "https://www.golfchannel.com/api/v2/tours/%d/events/%d" % (1, year))

    major_results = [Tournament(year=year, channel_tid=e['key'], tournament_name=e['name'])
                     for e in func_find(api_events, lambda event: event['major'] and 'players' not in event['name'], limit=4)]

    print([(m.channel_tid, m.name) for m in major_results])
    assert len(major_results) == 4
    assert all(['players' not in m.name.lower() for m in major_results])

    return

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


def db_upload_standings_individual(channel_tid, tid, year, conn=None):
    conn = filter_conn(conn)

    tournament = get_api_tournament(channel_tid=channel_tid)
    tournament.tid = tid
    tournament.year = year
    calculate_api_standings(tournament, get_picks=True, conn=conn)

    conn.exec('INSERT INTO season VALUES (%s) ON CONFLICT DO NOTHING',
              (tournament.year,))  # Insert season

    conn.exec("DELETE FROM event_standings_xref CASCADE WHERE tournament_id=%s AND season_year=%s",
              (tournament.tid, tournament.year))
    conn.exec('INSERT INTO event (tournament_id, season_year) VALUES (%s, %s) ON CONFLICT DO NOTHING',
              (tournament.tid, tournament.year))  # Insert season

    standings_insert_query = "INSERT INTO event_standings_xref (tournament_id, season_year, pickset_id, position, points) VALUES "

    for pickset in tournament.picksets:
        values_query = conn.cur.mogrify(" (%s,%s,%s,%s,%s),",
                                        (tournament.tid, tournament.year, pickset.id, pickset.pos, pickset.points))
        standings_insert_query += values_query.decode()

    conn.exec(standings_insert_query[:-1] + " ON CONFLICT DO NOTHING")

    conn.commit()


def db_set_photo_urls(conn=None):
    conn = filter_conn(conn)
    db_players = conn.exec_fetch(
        "SELECT id, name FROM player WHERE tour_id is NULL")
    api_players = request_json(Player.ALL_PLAYERS_URL)['plrs']

    for player in db_players:
        match = func_find(api_players, lambda pl: ' '.join(
            (pl['nameF'], pl['nameL'])).lower() == player['name'].lower())
        if match is not None:
            pid = match['pid']
            conn.exec("UPDATE player SET tour_id = %s, photo_url = %s WHERE id=%s",
                      (pid, Player.PGA_PHOTO_URL % pid, player['id']))

    conn.commit()


def check_levels_good(levels):
    # flattened_levels = [pl for level in levels for pl in level]
    owgr_data = requests.get(Player.STATS_URL %
                             Player.OWGR_STAT_ID).json()[:100]
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
    # insert_levels(CURRENT_YEAR)
    con = Conn()
    for channel_tid, tid in []:
        tournament = Tournament(channel_tid=channel_tid, tid=tid, year=2021)
        db_upload_standings_individual(tournament, conn=con)
        db_upload_leaderboard_individual(channel_tid, tid, 2021, conn=con)
