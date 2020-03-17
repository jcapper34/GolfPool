from flask import Blueprint, render_template

results_mod = Blueprint("results", __name__, template_folder='templates')   # Register blueprint

# Root of Results Module
@results_mod.route("/")
def results_index():
    return "Hello picks"

# Live Standings
@results_mod.route("/live")
def results_live():
    return "TODO"