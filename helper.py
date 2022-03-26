import json
import inspect
from pprint import pprint
from datetime import datetime
from typing import Dict

import requests

""" FUNCTIONS """
def splash(obj):
    if isinstance(obj, list):
        obj = [val.__str__() for val in obj]
    elif isinstance(obj, dict):
        obj = {key: val.__str__() for key, val in obj.items()}

    pprint(obj)


def func_find(obj, func, limit=1, get_index=False):
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


def request_json(url) -> Dict:
    try:
        if 'http' in url.lower():
            return requests.get(url).json()
    except json.JSONDecodeError as e:
        raise

    with open(url) as f:
        return json.load(f)


def obj_to_json(obj) -> str:
    attributes = inspect.getmembers(obj, lambda a: not(inspect.isroutine(a)))
    properties = {a[0]: a[1] for a in attributes if not(
        a[0].startswith('__') and a[0].endswith('__'))}
    return json.dumps(properties)

 
""" CONSTANTS """
CURRENT_YEAR = int(datetime.now().year)
