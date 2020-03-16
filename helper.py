from pprint import pprint
from datetime import datetime

def splash(obj):
    if isinstance(obj, list):
        obj = [val.__str__() for val in obj]
    elif isinstance(obj, dict):
        obj = {key:val.__str__() for key, val in obj.items()}

    pprint(obj)


### CONSTANTS ###
NOW = datetime.now()
CURRENT_YEAR = int(NOW.year)