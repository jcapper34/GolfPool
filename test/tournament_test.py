import os
import sys

from tournament.tournament_retriever import get_db_rankings, get_db_standings

APP_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, APP_ROOT)

### Start Test Script Here ###
from helper.helpers import splash
import requests
from tournament.tournament import Tournament


def test_fill_db_rankings(year=2019, tid='014', conn=None):
    splash(get_db_rankings(tid, year, conn=conn))


def test_fill_db_standings(year=2019, tid='014', conn=None):
    splash(get_db_standings(tid, year, conn=conn))

