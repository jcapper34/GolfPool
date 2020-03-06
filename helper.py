from pprint import pprint

def splash(obj):
    if isinstance(obj, list):
        obj = [val.__str__() for val in obj]
    elif isinstance(obj, dict):
        obj = {key:val.__str__() for key, val in obj.items()}

    pprint(obj)