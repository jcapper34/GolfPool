import json
import inspect
from pprint import pprint
from datetime import datetime
import threading
import time
from typing import Any, Dict

import requests

from config import TOUR_PHOTO_URL

""" FUNCTIONS """
def splash(obj) -> None:
    if isinstance(obj, list):
        obj = [val.__str__() for val in obj]
    elif isinstance(obj, dict):
        obj = {key: val.__str__() for key, val in obj.items()}

    pprint(obj)


def func_find(obj, func, limit=1, get_index=False) -> Any:
    found = []
    num_found = 0
    for i in range(len(obj)):
        thing = obj[i]
        if func(thing):
            if get_index:
                found.append(i)
            else:
                found.append(thing)
            num_found += 1
            if num_found == limit:
                break

    if not found:
        return None

    if limit == 1:
        return found[0]

    return found

http_lock = threading.Lock()
def request_json(url) -> Dict:
    """
    Thread-safe way to get json via http or locally
    """
    global http_lock
    def process_http_raw(url):
        with http_lock:
            return requests.get(url).json()
    
    # Do http request
    if 'http' in url.casefold():
        return retry_util(lambda: process_http_raw(url))
    
    with open(url) as f:
        return json.load(f)


def obj_to_json(obj) -> str:
    attributes = inspect.getmembers(obj, lambda a: not(inspect.isroutine(a)))
    properties = {a[0]: a[1] for a in attributes if not(
        a[0].startswith('__') and a[0].endswith('__'))}
    return json.dumps(properties)


def resolve_photo(channel_photo, tour_id) -> str:
    """
    If tour_id is not null, then use the tour photo. Otherwise use channel photo
    """
    if tour_id is None:
        return channel_photo
    
    return TOUR_PHOTO_URL % tour_id


def retry_util(func, max_retry=3, wait_sec=2) -> None:
    """
    Retry a function until success or max retries has been exceeded
    """
    for attempt in range(max_retry):
        try:
            return func()
        except Exception:
            time.sleep(wait_sec)


def default_to(val, default):
    """
    Return default if val is None
    """
    if val is None:
        return default
    
    return val


""" CONSTANTS """
CURRENT_YEAR = int(datetime.now().year)
