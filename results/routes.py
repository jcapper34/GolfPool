from flask import Blueprint, render_template, request, get_template_attribute

from db.conn import Conn
from helper import func_find
from picksets.pickset import Pickset
from picksets.picksets_db import get_all_picks
from tournament.tournament import Tournament

results_mod = Blueprint("results", __name__, template_folder='templates', static_folder='static')   # Register blueprint

# Root of Results Module
@results_mod.route("/")
@results_mod.route("/live")
def results_live():
    # TODO: Live Results. Should be fun lol
    return "Hello picks"


# Past Standings
@results_mod.route("/<int:year>/<tid>")
def results_past(year, tid):
    conn = Conn()

    # Get Database Standings
    tournament = Tournament()
    tournament.fill_db_rankings(year, tid, conn=conn)
    tournament.fill_db_standings(year, tid, conn=conn)

    # Merge all picks with tournament
    all_picks = get_all_picks(year, conn=conn)
    tournament.merge_all_picks(all_picks)

    return render_template('standings.html', tournament=tournament)


# Past Standings
@results_mod.route("/<int:year>/<tid>/get-pickset-modal")
def get_pickset_modal(year, tid):
    psid = request.args.get("psid")

    conn = Conn()

    # Get Database Standings
    tournament = Tournament()
    tournament.fill_db_rankings(year, tid, conn=conn)

    # Get Pickset
    pickset = Pickset(psid=psid)
    pickset.fill_picks(conn=conn)

    # Get Tournament results for each picked player
    for level_players in pickset.picks:
        for player in level_players:
            pl = func_find(tournament.players, lambda p: p.id == player.id)
            if pl is None:  # If not found
                continue

            player.pos = pl.pos
            player.points = pl.points
            player.total = pl.total

    pickset_modal = get_template_attribute("modal.macro.html", "pickset_modal")
    return pickset_modal(pickset)
