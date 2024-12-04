from dataclasses import asdict
from flask import blueprints
from flask.json import jsonify
from config import PICKS_LOCKED, UNLOCK_ALL_PAGES
from helpers import CURRENT_YEAR

from picksets.pickset_getters import get_all_picks
from tournament.tournament_calculations import calculate_standings
from tournament.tournament_retriever import get_api_tournament


mod = blueprints.Blueprint("rest", __name__)


@mod.route("/picks/<int:year>")
def get_json_picks(year=CURRENT_YEAR):
    # Make sure you don't show picks of current year unless picks are locked
    if not UNLOCK_ALL_PAGES:
        if year == CURRENT_YEAR and not PICKS_LOCKED:
            year = CURRENT_YEAR - 1
    
    all_picks = get_all_picks(year)
    return jsonify([asdict(pickset) for pickset in all_picks])


@mod.route("/results/live")
def get_json_live_results():
    # Make sure you don't show results of current year unless picks are locked
    if not UNLOCK_ALL_PAGES:
        if year == CURRENT_YEAR and not PICKS_LOCKED:
            year = CURRENT_YEAR - 1
    
    tournament = get_api_tournament()
    tournament.picksets = calculate_standings(tournament.players, get_all_picks(year))
    return jsonify(asdict(tournament))

