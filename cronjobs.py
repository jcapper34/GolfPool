from datetime import datetime, timedelta
import os
import shutil
from threading import Thread
from dateutil.parser import isoparse

import logging
from pytz import timezone
from apscheduler.schedulers.background import BackgroundScheduler
import requests
from config import *
from db.connection_pool import db_pool
from helper.globalcache import GlobalCache
from helpers import *
from picksets.pickset_getters import get_all_picks
from players.player_getters import get_levels_db
from tournament.tournament_calculations import calculate_standings
from tournament.tournament_retriever import get_api_tournament


def start_jobs() -> None:
    """
    Starts the Database Jobs
    """
    scheduler = BackgroundScheduler(timezone=timezone("US/Pacific"))

    def start_and_schedule(func, trigger, day_of_week, hour):
        # Call job async
        Thread(target=func, args=[]).start()

        # Add job to scheduler
        scheduler.add_job(
            func, trigger=trigger, day_of_week=day_of_week, hour=hour)

    start_and_schedule(xl_cleanup_job, trigger='cron', day_of_week='*', hour='*')
    start_and_schedule(update_current_major, trigger='cron', day_of_week='*', hour='0')

    # Start Periodic Scheduler
    scheduler.start()

def resolve_major(title) -> str:
    """
    Sloppy way of determining the tid from the tournament name
    """
    title = title.casefold()
    if "Masters Tournament".casefold() == title:
        return '014'
    elif "U.S. Open".casefold() == title:
        return '026'
    elif "The Open Championship".casefold() in title:
        return '100'
    elif "PGA Championship".casefold() == title:
        return '033'

    return None

def update_current_major(year=CURRENT_YEAR) -> None:
    events = requests.get(EVENTS_URL % year).json().get("data", [])
    now = datetime.now()
    for event in events:
        name = event.get("tournamentName")
        tid = resolve_major(name)
        if tid is not None:
            eventStart = isoparse(event.get("startDate"))
            eventEnd = isoparse(event.get("endDate"))
            if now < eventEnd + timedelta(days=1):
                GlobalCache.set_live_tournament(name, event.get("tournamentId"), year)
                return

def upload_last_major(year=CURRENT_YEAR) -> None:
    """
    _summary_
    """

    dt = datetime.now()
    events = requests.get(EVENTS_URL % year).json().get("data", [])
    logging.info("[update_last_major] Found %d events from API in year %d" % (len(events), year))

    # Walk through events backwards to find majors
    major_golfcom_ids = []
    for event in reversed(events):
        if event.get("major"):
            golfcom_id = event.get("key")
            tid = resolve_major(event.get("name"))
            eventStart = isoparse(event.get("startDate"))
            eventEnd = isoparse(event.get("endDate"))

            major_golfcom_ids.append(golfcom_id)

            if event.get("winnerKey"):
                with db_pool.get_conn() as conn:
                    inDb = conn.exec_fetch(
                        "SELECT EXISTS (SELECT FROM event_leaderboard_xref WHERE tournament_id=%s AND season_year=%s)", (tid, eventEnd.year), fetchall=False)[0]
                    if not inDb:
                        logging.info("[update_last_major] %s is being uploaded to DB" % event.get("name"))
                        tournament = get_api_tournament(golfcom_id)

                        # Insert season
                        conn.exec(
                            "INSERT INTO season VALUES (%s) ON CONFLICT DO NOTHING", (eventEnd.year,))

                        # Insert Event
                        conn.exec('INSERT INTO event (tournament_id, season_year) VALUES (%s, %s) ON CONFLICT DO NOTHING',
                                (tid, year))  # Insert event

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
                        picksets = calculate_standings(tournament.players, get_all_picks(year))
                        standings_insert_query = "INSERT INTO event_standings_xref (tournament_id, season_year, pickset_id, position, points) VALUES "

                        standings_insert_query += ','.join((conn.cur.mogrify(" (%s,%s,%s,%s,%s)",
                                                    (tid, year, pickset.id, pickset.pos, pickset.points)).decode()
                                                for pickset in picksets))

                        
                        conn.exec(standings_insert_query)
                        conn.commit()
                        logging.info("[update_last_major] %s was uploaded to DB", event.get("name"))

                    else:
                        logging.info("[update_last_major] %s is already in DB", event.get("name"))

            # Set the tournament_id of the current major
            if dt > eventStart:
                GlobalCache.set_live_tournament(golfcom_id, year)
        
    # Default current_tid to be the first major of the year
    if GlobalCache.live_tournament is None:
        GlobalCache.set_live_tournament(major_golfcom_ids.pop(), year)

    logging.info("[update_last_major] Current tid set to %s" % GlobalCache.live_tournament.tid)
    logging.info("[update_last_major] Finished job")

def xl_cleanup_job() -> None:
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
    
    logging.info("[xl_cleanup] Finished job")
