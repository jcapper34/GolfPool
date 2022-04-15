from datetime import datetime
from pprint import pprint
from threading import Thread
from dateutil.parser import isoparse

import logging
from pytz import timezone
from apscheduler.schedulers.background import BackgroundScheduler
import requests
from config import EVENTS_URL
from db.conn import Conn
from db.db_helper import filter_conn
from globalcache import GlobalCache
from helper import CURRENT_YEAR
from tournament.tournament_calculations import calculate_api_standings
from tournament.tournament_retriever import get_api_tournament


def start_jobs():
    """
    Starts the Database Jobs
    """
    scheduler = BackgroundScheduler(timezone=timezone("US/Pacific"))

    # Call job async
    Thread(target=update_last_major, args=[]).start()

    # Add Jobs
    job = scheduler.add_job(
        update_last_major, trigger='cron', day_of_week='0,6', hour='*')

    # Start Periodic Scheduler
    scheduler.start()


def resolve_major(title):
    """
    Pretty sloppy way of determining the tid from the major name
    """
    title = title.lower()
    if "masters" in title:
        tid = '014'
    elif ("us" in title or 'u.s' in title) and 'open' in title:
        tid = '026'
    elif 'open' in title:
        tid = '100'
    else:
        tid = '033'

    return tid


def update_last_major():
    """
    _summary_
    """

    dt = datetime.now()
    events = requests.get(EVENTS_URL % CURRENT_YEAR).json()

    for event in reversed(events):
        if event.get("major"):
            channel_tid = event.get("key")
            tid = resolve_major(event.get("name"))
            eventStart = isoparse(event.get("startDate"))
            eventEnd = isoparse(event.get("endDate"))

            if event.get("winnerKey"):
                conn = Conn()

                inDb = conn.exec_fetch(
                    "SELECT EXISTS (SELECT 1 FROM event_leaderboard_xref WHERE tournament_id=%s AND season_year=%s)", (tid, eventEnd.year), fetchall=False)[0]
                if not inDb:
                    print(event.get("name"), "is being uploaded to DB")
                    tournament = get_api_tournament(channel_tid)

                    # Insert season
                    conn.exec(
                        "INSERT INTO season VALUES (%s) ON CONFLICT DO NOTHING", (eventEnd.year,))
                    
                    # Insert Event
                    conn.exec('INSERT INTO event (tournament_id, season_year) VALUES (%s, %s) ON CONFLICT DO NOTHING',
                              (tid, eventEnd.year))  # Insert event
                    
                    # Insert the leaderboard entries
                    leaderboard_insert_query = "INSERT INTO event_leaderboard_xref (tournament_id, season_year, position, score, points, player_id) VALUES "
                    for player in tournament.players:
                        conn.exec("INSERT INTO player (id, name) VALUES (%s,%s) ON CONFLICT DO NOTHING",
                                  (player.id, player.name))
                        values_query = conn.cur.mogrify(" (%s,%s,%s,%s,%s,%s),",
                                                        (tid, eventEnd.year, player.pos, player.total, player.points, player.id))
                        leaderboard_insert_query += values_query.decode()

                    conn.exec(leaderboard_insert_query[:-1])
                    
                    # Insert standings entries
                    calculate_api_standings(tournament, get_picks=True, conn=conn)
                    standings_insert_query = "INSERT INTO event_standings_xref (tournament_id, season_year, pickset_id, position, points) VALUES "

                    for pickset in tournament.picksets:
                        values_query = conn.cur.mogrify(" (%s,%s,%s,%s,%s),",
                                                        (tid, eventEnd.year, pickset.id, pickset.pos, pickset.points))
                        standings_insert_query += values_query.decode()

                    conn.exec(standings_insert_query[:-1])
                    conn.commit()
                    logging.info("%s was uploaded to DB", event.get("name"))

                else:
                    logging.info("%s is already in DB", event.get("name"))

            if dt > eventStart:
                GlobalCache.current_tid = channel_tid
                break

    logging.info("Cron Job Finished")
