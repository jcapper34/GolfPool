import json
import inspect
import logging
from pprint import pprint
from datetime import datetime
import threading
import time
from typing import Any, Dict

import requests
from unidecode import unidecode

from config import BROWSER_EMULATE_HEADERS, TOUR_PHOTO_URL

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
    def process_http_raw(url, include_browser_headers=True):
        with http_lock:
            return requests.get(
                url, 
                headers=BROWSER_EMULATE_HEADERS if include_browser_headers else None).json()
    
    # Do http request
    if url.casefold().startswith("http"):
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
    attempt = 0
    while True:
        try:
            return func()
        except Exception as e:
            if attempt < max_retry:
                logging.error("[retry_util] Received exception %s. Retrying...", type(e))
                time.sleep(wait_sec)
                attempt += 1
            else:
                raise e

def default_to(val, default):
    """
    Return default if val is None
    """
    if val is None:
        return default
    
    return val

def name_match(a, b):
    """
    Are two strings the same name
    """

    def nickname_convert(name):
        nickname_mapper = {
            "matt": "matthew",
            "sam": "samuel",
            "alex": "alexander",
            "ben": "benjamin",
            "cam": "cameron",
            "dan": "daniel",
            "mike": "michael",
            "jeff": "jeffrey",
            "joe": "joseph"
        }
        name_separated = name.split(' ')
        first_name = name_separated[0]
        if first_name in nickname_mapper:
            name_separated[0] = nickname_mapper[first_name]

        return ' '.join(name_separated)

    def name_normalize(name):
        for c in ('-', '\'', '.', ','):
            name = name.replace(c, '')
        return unidecode(nickname_convert(name.casefold()))

    return name_normalize(a) == name_normalize(b)

""" CONSTANTS """
# CURRENT_YEAR = int(datetime.now().year)
CURRENT_YEAR = 2025
