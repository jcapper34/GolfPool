from flask import blueprints
from flask.json import jsonify
from requests import api
from helper import CURRENT_YEAR

from picksets.picksets_db import get_all_picks


api_mod = blueprints("rest", __name__)

@api_mod.route("/picks/<int:year>")
def get_picks(year=CURRENT_YEAR):
    all_picks = get_all_picks(year)
    return jsonify()

