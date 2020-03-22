from pprint import pprint
from datetime import datetime

""" FUNCTIONS """
def splash(obj):
    if isinstance(obj, list):
        obj = [val.__str__() for val in obj]
    elif isinstance(obj, dict):
        obj = {key:val.__str__() for key, val in obj.items()}

    pprint(obj)

def func_find(obj, func, limit=1):
    found = []
    num_found = 0
    for thing in obj:
        if func(thing):
            found.append(thing)
            num_found += 1
            if num_found == limit:
                break

    if not found:
        return None

    if limit == 1:
        return found[0]

    return found


""" CONSTANTS """
NOW = datetime.now()
CURRENT_YEAR = int(NOW.year)
# CURRENT_YEAR = 2020