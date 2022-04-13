from datetime import datetime
from dateutil.parser import isoparse

import logging
from pytz import timezone
from apscheduler.schedulers.background import BackgroundScheduler
import requests
from config import ACTIVE_EVENTS_URL, EVENTS_URL
from db.db_helper import filter_conn
from globalcache import GlobalCache
from helper import CURRENT_YEAR
from tournament.tournament_retriever import get_api_tournament

def print_job():
    """
    Test Job
    """
    logging.info("JOB RAN")


def start_jobs(conn=None):
    """
    Starts the Database Jobs
    """
    conn = filter_conn(conn)
    scheduler = BackgroundScheduler(timezone=timezone("US/Pacific"))
    
    # Add Jobs
    fetch_last_major()
    job = scheduler.add_job(fetch_last_major, trigger='cron', day_of_week='0,6', hour='*')
    
    # Start Periodic Scheduler
    scheduler.start()
    

def fetch_last_major():
    """
    _summary_
    """
    dt = datetime.now()
    events = requests.get(EVENTS_URL % CURRENT_YEAR).json()
    
    for event in reversed(events):
        if dt > isoparse(event.get("startDate")) and event.get("major"):
            GlobalCache.current_tid = event.get("key")
            break
            