from dataclasses import asdict
import json
from flask import blueprints
from flask.json import jsonify
from requests import api
from helper import CURRENT_YEAR

from picksets.pickset_getters import get_all_picks
from tournament.tournament_calculations import calculate_api_standings
from tournament.tournament import Tournament
from tournament.tournament_retriever import get_api_tournament


mod = blueprints.Blueprint("rest", __name__)

@mod.route("/picks/<int:year>")
def get_json_picks(year=CURRENT_YEAR):
    all_picks = get_all_picks(year)
    return jsonify([asdict(pickset) for pickset in all_picks])


@mod.route("/results/live")
def get_json_live_results():
    tournament = get_api_tournament()
    calculate_api_standings(tournament, year=CURRENT_YEAR)
    return jsonify(asdict(tournament))

