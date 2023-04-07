import os
import sys
import requests
from tabulate import tabulate

base_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(base_dir + "/..") # Hack to import from root

from config import OWGR_STAT_ID, STATS_URL
from helper.helpers import CURRENT_YEAR, func_find
from db.connection_pool import db_pool
from players.player_getters import get_levels_db
from picksets.pickset_submission import db_insert_picks, db_inserts
from players.player import Player
from tournament.tournament_retriever import get_api_tournament
from tournament.tournament_calculations import calculate_standings
from picksets.pickset_getters import get_all_picks

def check_levels_good(levels, year):
    """
        levels should be a list of list of pid
    """
    # flattened_levels = [pl for level in levels for pl in level]
    owgr_data = requests.get(STATS_URL % (OWGR_STAT_ID, year)).json()[:100]
    table = []
    for i, player in enumerate(owgr_data, start=1):
        p_name = player['firstName'] + " " + player['lastName']
        api_pid = str(player.get('golferId'))
        found = False
        for level in levels:
            if func_find(level, lambda pid: api_pid == pid):
                table.append((i, p_name, levels.index(level)+1))
                found = True

        if not found:
            table.append((i, p_name, "-"))
    
    print(tabulate(table))


def insert_levels(filename, year):
    with open(filename, "r") as f:
        lines = f.readlines()
    
    current_level = 1
    levels = [[], [], []]
    for line in lines:
        line = line.strip()
        if not line:
            current_level += 1
        else:
            levels[current_level-1].append(line)
    
    for n, level in enumerate(levels, start=1):
        print(n, level)

    assert len(levels) == 3

    with db_pool.get_conn() as conn:
        # Do clean up
        conn.exec("DELETE FROM level_xref WHERE season_year = %s", (year,))
        conn.exec("DELETE FROM pickset WHERE season_year = %s", (year,))

        # Insert season
        conn.exec("INSERT INTO season VALUES (%s) ON CONFLICT DO NOTHING", (year,))

        levels_pid = []
        for level_num in range(1, len(levels)+1):
            pids = []
            for player_name in levels[level_num-1]:
                results = conn.exec_fetch(
                    "SELECT id FROM player WHERE name=%s", (player_name,), fetchall=False)    # Get player id
                if results is None:
                    print("Player %s does not exist" % player_name)
                    continue
                pid = results[0]
                conn.exec(
                    "INSERT INTO level_xref (player_id, season_year, level) VALUES(%s,%s,%s)", (pid, year, level_num))
                pids.append(pid)

            levels_pid.append(pids)

        check_levels_good(levels_pid, year)

        # conn.commit()


def parse_xl(filename, year):
    with open(filename, "r", encoding='utf-8') as f:
        lines = f.readlines()
    
    with db_pool.get_conn() as conn:
        participants = conn.exec_fetch("SELECT * FROM participant")

        # Remove existing entries
        conn.exec("DELETE FROM pickset where season_year = %s", (year,))

        for line in lines:
            columns = line.split('\t')
            assert len(columns) == 11

            participant_name = columns[0]
            level1 = columns[1:4]
            level2 = columns[4:7]
            level3 = columns[7:9]
            level4 = columns[9:11]

            # Validate the picked players
            picked_players = []
            for n, level in enumerate([level1, level2, level3, level4], start=1):
                for player_name in level:
                    player_name = player_name.strip()
                    results = conn.exec_fetch(
                        "SELECT id FROM player WHERE name=%s", (player_name,), fetchall=False)    # Get player id
                    if results is None:
                        print("Player %s does not exist" % player_name)
                        raise Exception
                    else:
                        # Happy flow
                        picked_players.append(Player(id=results[0], name=player_name))

            # If participant exists
            participant = func_find(participants, lambda p: participant_name.casefold() == p['name'].casefold())
            if participant is None:
                print("No participant named %s in database" % participant_name)
                raise Exception
            else:
                if len(picked_players) == 10:
                    results = conn.exec_fetch("""
                        INSERT INTO pickset (participant_id, season_year) VALUES (%s,%s)
                            RETURNING id
                    """, (participant['id'], year))
                    psid = results[0][0]

                    """ Insert picks """
                    db_insert_picks(psid, picked_players, conn=conn)
                    print("Uploaded pickset for %s" % participant_name)

        conn.commit()

             
def grab_players_from_db():
    with db_pool.get_conn() as conn:
        return conn.exec_fetch("SELECT * FROM player")


def upload_tournament():
    tournament_meta = [
        # ("014", "17370", 2018),
        # ("014", "17893", 2019),
        # ("014", "18491", 2020),
        # ("014", "19208", 2021),
        # ("014", "19540", 2022),

        # ("026", "17380", 2018),
        # ("026", "17902", 2019),
        # ("026", "18501", 2020),
        # ("026", "19207", 2021),
        # ("026", "19550", 2022),

        # ("100", "17386", 2018),
        # ("100", "17908", 2019),
        # ("100", "18507", 2020), # Cancelled
        # ("100", "19198", 2021),
        # ("100", "19556", 2022),

        # ("033", "17390", 2018),
        # ("033", "17898", 2019),
        # ("033", "18496", 2020),
        # ("033", "19190", 2021),
        # ("033", "19546", 2022),
    ]

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
    
    with db_pool.get_conn() as conn:
        for tid, channel_tid, year in tournament_meta:
            conn.exec("DELETE FROM event WHERE tournament_id=%s AND season_year=%s", (tid, year))

            tournament = get_api_tournament(channel_tid, year)
            print("%s %d is being uploaded to DB" % (tournament.name, year))

            # Insert season
            conn.exec(
                "INSERT INTO season VALUES (%s) ON CONFLICT DO NOTHING", (year,))

            # Insert Event
            conn.exec('INSERT INTO event (tournament_id, season_year) VALUES (%s, %s)',
                    (tid, year))  # Insert event

            # Insert the leaderboard entries
            leaderboard_insert_query = "INSERT INTO event_leaderboard_xref (tournament_id, season_year, position, score, points, player_id) VALUES "
            for player in set(tournament.players):
                conn.exec("INSERT INTO player (id, name) VALUES (%s,%s) ON CONFLICT DO NOTHING",
                        (player.id, player.name))
                values_query = conn.cur.mogrify(" (%s,%s,%s,%s,%s,%s),",
                                                (tid, year, player.pos, player.total, player.points, player.id))
                leaderboard_insert_query += values_query.decode()

            conn.exec(leaderboard_insert_query[:-1])

            # Insert standings entries
            picksets = calculate_standings(tournament.players, get_all_picks(year))
            standings_insert_query = "INSERT INTO event_standings_xref (tournament_id, season_year, pickset_id, position, points) VALUES "

            standings_insert_query += ','.join((conn.cur.mogrify(" (%s,%s,%s,%s,%s)",
                                        (tid, year, pickset.id, pickset.pos, pickset.points)).decode()
                                    for pickset in picksets))

            
            conn.exec(standings_insert_query)
            print("%s - %d was uploaded to DB" % (tid, year))
            
        conn.commit()


def put_level_limits(limits, year):
    with db_pool.get_conn() as conn:
        for level_num, limit in enumerate(limits, start=1):
            conn.exec("INSERT INTO level_limit_xref (level, pick_limit, season_year) VALUES (%s,%s,%s)", (level_num, limit, year))
            print("Inserted", (level_num, limit, year))
        
        conn.commit()


if __name__ == '__main__':
    pass
