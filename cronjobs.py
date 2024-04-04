from datetime import datetime, timedelta
import os
import shutil
from threading import Thread
from dateutil.parser import isoparse

import logging
from pytz import timezone
from apscheduler.schedulers.background import BackgroundScheduler
import requests
from config import EVENTS_URL, INDIVIDUAL_GOLFER_URL, TOUR_PLAYERS_URL, XL_DIR
from db.connection_pool import db_pool
from helper.globalcache import GlobalCache
from helper.helpers import CURRENT_YEAR, func_find, request_json
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
    title = title.casefold()
    if "masters" in title:
        tid = '014'
    elif ("us" in title or 'u.s' in title) and 'open' in title:
        tid = '026'
    elif 'open' in title:
        tid = '100'
    else:
        tid = '033'

    return tid


def update_last_major(year=CURRENT_YEAR) -> None:
    """
    _summary_
    """

    dt = datetime.now()
    events = requests.get(EVENTS_URL % year).json()
    logging.info("[update_last_major] Found %d events from API in year %d" % (len(events), year))

    # Walk through events backwards to find majors
    major_channel_tids = []
    for event in reversed(events):
        if event.get("major"):
            channel_tid = event.get("key")
            tid = resolve_major(event.get("name"))
            eventStart = isoparse(event.get("startDate"))
            eventEnd = isoparse(event.get("endDate"))

            major_channel_tids.append(channel_tid)

            if event.get("winnerKey"):
                with db_pool.get_conn() as conn:
                    inDb = conn.exec_fetch(
                        "SELECT EXISTS (SELECT FROM event_leaderboard_xref WHERE tournament_id=%s AND season_year=%s)", (tid, eventEnd.year), fetchall=False)[0]
                    if not inDb:
                        logging.info("[update_last_major] %s is being uploaded to DB" % event.get("name"))
                        tournament = get_api_tournament(channel_tid)

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
                GlobalCache.set_live_tournament(channel_tid, year)
        
    # Default current_tid to be the first major of the year
    if GlobalCache.live_tournament is None:
        GlobalCache.set_live_tournament(major_channel_tids.pop(), year)

    logging.info("[update_last_major] Current tid set to %s" % GlobalCache.live_tournament.tid)
    logging.info("[update_last_major] Finished job")


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
    
    logging.info("[xl_cleanup] Finished job")


def backfill_photos() -> None:
    with db_pool.get_conn() as conn:
        players = conn.exec_fetch("SELECT * FROM player WHERE photo_url is NULL")

        # Batch if necessary
        batch_size = 20
        if len(players) >= batch_size:
            players = players[:batch_size]

        num_updates = 0
        for player in players:
            player_json = request_json(INDIVIDUAL_GOLFER_URL % player['id'])
            photo_url = player_json.get("bioImageUrl")
            if photo_url is not None:
                conn.exec("UPDATE player SET photo_url = %s WHERE id = %s", (photo_url, player['id']))
                logging.info("[backfill_photos] Update photo for %s", player['name'])
                num_updates += 1
        
        if players:
            conn.commit()
            logging.info("[backfill_photos] Committed %d player photos to database" % num_updates)
        
        logging.info("[backfill_photos] Finished job")


def backfill_tour_ids() -> None:
    players_json = request_json(TOUR_PLAYERS_URL).get('plrs', [])
    logging.info("[backfill_tour_ids] Fetched %d players from PGA Tour API" % len(players_json))

    with db_pool.get_conn() as conn:
        db_players = conn.exec_fetch("SELECT * FROM player WHERE tour_id is NULL")
        player_hash = {p['name'].casefold():p['id'] for p in db_players}
        logging.info("[backfill_tour_ids] Fetched %d players from database" % len(db_players))

        # Batch if necessary
        batch_size = 100
        if len(db_players) >= batch_size:
            db_players = db_players[:batch_size]

        num_updates = 0
        for api_player in players_json:
            tour_id = api_player.get('pid')
            api_name = ' '.join([api_player.get('nameF'), api_player.get('nameL')])
            if api_name.casefold() in player_hash:
                db_player_id = player_hash[api_name.casefold()]
                conn.exec("UPDATE player SET tour_id = %s WHERE id = %s", (tour_id, db_player_id))
                logging.info("[backfill_tour_ids] Updated tour id for %s", api_name)
                num_updates += 1
        
        conn.commit()
        logging.info("[backfill_tour_ids] Committed %d player tour id to database" % num_updates)
        logging.info("[backfill_tour_ids] Finished job")
