from flask import Blueprint, render_template

results_mod = Blueprint("results", __name__, template_folder='templates')   # Register blueprint

# Root of Results Module
@results_mod.route("/")
@results_mod.route("/live")
def results_live():
    return "Hello picks"


# Past Standings
@results_mod.route("/<int:year>/<tid>")
def result_history(year, tid):
    return str(year) + tid