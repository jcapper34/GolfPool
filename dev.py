from helper import CURRENT_YEAR
from db.conn import Conn


def insert_levels(year=CURRENT_YEAR):
    levels = [
        [],
        [],
        []
    ]