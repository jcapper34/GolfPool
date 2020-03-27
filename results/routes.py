from flask import Blueprint, render_template, request, get_template_attribute, jsonify

from db.conn import Conn
from helper import func_find, CURRENT_YEAR
from picksets.pickset import Pickset
from picksets.picksets_db import get_all_picks
from players.player import Player
from tournament.tournament import Tournament

results_mod = Blueprint("results", __name__, template_folder='templates', static_folder='static')   # Register blueprint

""" LIVE ROUTES """
# Root of Results Module
@results_mod.route("/")
@results_mod.route("/live")
def results_live():
    tournament = Tournament()
    tournament.fill_api_leaderboard()
    tournament.calculate_api_standings()
    if request.args.get("refresh") is not None:    # If refresh
        standings_macro = get_template_attribute("standings.macro.html", "standings_table")
        leaderboard_macro = get_template_attribute("standings.macro.html", "leaderboard_table")
        return jsonify([standings_macro(tournament.picksets), leaderboard_macro(tournament.players)])

    return render_template('standings-live.html', tournament=tournament, event_years=Tournament.get_event_years())



""" PAST ROUTES """

# Past Standings
@results_mod.route("/<int:year>/<tid>")
def results_past(year, tid):
    conn = Conn()

    # Get Database Standings
    tournament = Tournament()
    if not tournament.fill_db_rankings(year, tid, conn=conn):   # If tournament not found in DB
        return render_template("locked-page.html", title='Golf Pool | Locked Tournament')

    tournament.fill_db_standings(year, tid, conn=conn)

    # Merge all picks with tournament
    all_picks = get_all_picks(year, conn=conn)
    tournament.merge_all_picks(all_picks)

    return render_template('standings-past.html', tournament=tournament, event_years=Tournament.get_event_years())


# Past Standings Pickset Modal
@results_mod.route("/<int:year>/<tid>/get-pickset-modal")
def get_pickset_modal(year, tid):
    psid = request.args.get("psid")

    conn = Conn()

    # Get Database Standings
    tournament = Tournament()
    tournament.fill_db_rankings(year, tid, conn=conn)

    # Get Pickset
    pickset = Pickset(psid=psid)
    pickset.fill_picks(separate=False, conn=conn)
    pickset.fill_tournament_history(year, conn=conn)

    # Get Tournament results for each picked player
    for player in pickset.picks:
        pl = func_find(tournament.players, lambda p: p.id == player.id)
        if pl is None:  # If not found
            player.points = 0
            continue

        player.pos = pl.pos
        player.points = pl.points
        player.total = pl.total

    pickset_modal = get_template_attribute("modal.macro.html", "pickset_modal")
    return pickset_modal(pickset)

@results_mod.route("/<int:year>/<tid>/get-player-modal")
def get_player_modal(year, tid):
    pid = request.args.get("pid")

    conn = Conn()

    player = Player(pid=pid)
    player.fill_tournament_data(tid=tid, year=year, conn=conn)
    player.fill_who_picked(year, conn=conn)

    player_modal = get_template_attribute("modal.macro.html", "player_modal")
    return player_modal(player)