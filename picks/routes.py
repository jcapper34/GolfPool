from flask import Blueprint, render_template, request
from helper import CURRENT_YEAR, splash
from picksets.picksets_submit import submit_picks
from players.players_db import get_levels
from players.player import Player

## Register Blueprint ##
picks_mod = Blueprint("picks", __name__, template_folder='templates', static_folder='static')


## ROUTES ##
# Root of Picks Module
@picks_mod.route("/")
def picks_index():
    return "Hello Picks"

# Make Picks Page
@picks_mod.route("/make")
def picks_make():
    return render_template("make/make-picks.html", level_players=get_levels(CURRENT_YEAR-1), OWGR_URL=Player.OWGR_URL % str(CURRENT_YEAR))


# Change Picks Page
@picks_mod.route("/change")
def picks_change():
    return "TODO"

# Picks Submission
@picks_mod.route("/submit", methods=['POST'])
def picks_submit():
    pickset = submit_picks(
        name=request.form.get("name").capitalize(),
        email=request.form.get("email"),
        pin=request.form.get("pin"),
        level_1=request.form.getlist("level-1"),
        level_2=request.form.getlist("level-2"),
        level_3=request.form.getlist("level-3"),
        level_4=None
    )
    return str(pickset)


# Poolwide Picks Page
@picks_mod.route("/poolwide")
def picks_poolwide():
    return "TODO"