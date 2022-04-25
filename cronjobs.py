from datetime import datetime, timedelta
import os
import shutil
from threading import Thread
from dateutil.parser import isoparse

import logging
from pytz import timezone
from apscheduler.schedulers.background import BackgroundScheduler
import requests
from config import EVENTS_URL, XL_DIR
from db.conn import Conn
from helper.globalcache import GlobalCache
from helper.helpers import CURRENT_YEAR
from picksets.pickset_getters import get_all_picks
from tournament.tournament_calculations import calculate_standings
from tournament.tournament_retriever import get_api_tournament


def start_jobs() -> None:
    """
    Starts the Database Jobs
    """
    scheduler = BackgroundScheduler(timezone=timezone("US/Pacific"))

    job_funcs = [update_last_major, xl_cleanup]
    for job_func in job_funcs:
        # Call job async
        Thread(target=job_func, args=[]).start()

        # Add Jobs
        job = scheduler.add_job(
            job_func, trigger='cron', day_of_week='0,6', hour='*')

    # Start Periodic Scheduler
    scheduler.start()


def resolve_major(title) -> str:
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


def update_last_major() -> None:
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
                              (tid, CURRENT_YEAR))  # Insert event

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
                    picksets = calculate_standings(tournament.players, get_all_picks(CURRENT_YEAR, conn=conn))
                    standings_insert_query = "INSERT INTO event_standings_xref (tournament_id, season_year, pickset_id, position, points) VALUES "

                    standings_insert_query += ','.join((conn.cur.mogrify(" (%s,%s,%s,%s,%s)",
                                                (tid, CURRENT_YEAR, pickset.id, pickset.pos, pickset.points)).decode()
                                               for pickset in picksets))

                    
                    conn.exec(standings_insert_query)
                    conn.commit()
                    logging.info("%s was uploaded to DB", event.get("name"))

                else:
                    logging.info("%s is already in DB", event.get("name"))

            if dt > eventStart:
                GlobalCache.current_tid = channel_tid
                break

    logging.info("Cron Job Finished")


def xl_cleanup() -> None:
    """
    Delete any excel generated files that are expired
    """
    
    expiration_delta = timedelta(hours=1)
    dt = datetime.now()
    
    if os.path.exists(XL_DIR):
        for filename in os.listdir(XL_DIR):
            filepath = os.path.join(XL_DIR, filename)
            if os.path.isdir(filepath):
                if os.path.getmtime(filepath) + expiration_delta.total_seconds() < dt.timestamp():
                    shutil.rmtree(filepath, ignore_errors=False, onerror=None)
