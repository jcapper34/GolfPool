from flask import Blueprint, render_template, request, get_template_attribute, jsonify, session

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
    tournament = Tournament(year=CURRENT_YEAR)
    tournament.fill_api_leaderboard()
    tournament.calculate_api_standings()
    if request.args.get("refresh") is not None:    # If refresh
        standings_macro = get_template_attribute("standings.macro.html", "standings_table")
        leaderboard_macro = get_template_attribute("standings.macro.html", "leaderboard_table")
        return jsonify([standings_macro(tournament.picksets), leaderboard_macro(tournament.players)])

    return render_template('standings-live.html', tournament=tournament, event_years=Tournament.get_event_years(), user_psid=session.get("psid"))


""" PAST ROUTES """

# Past Standings
@results_mod.route("/<int:year>/<tid>")
def results_past(year, tid):
    conn = Conn()

    # Get Database Standings
    tournament = Tournament(year=year, tid=tid)
    if not tournament.fill_db_rankings(conn=conn):   # If tournament not found in DB
        return render_template("locked-standings.html", tournament=tournament, event_years=Tournament.get_event_years())

    tournament.fill_db_standings(conn=conn)

    # Merge all picks with tournament
    all_picks = get_all_picks(year, conn=conn)
    tournament.merge_all_picks(all_picks)

    return render_template('standings-past.html', tournament=tournament, event_years=Tournament.get_event_years(), user_psid=session.get("psid"))


# Past Standings Pickset Modal
@results_mod.route("/get-pickset-modal")
@results_mod.route("/live/get-pickset-modal")
@results_mod.route("/<int:year>/<tid>/get-pickset-modal")
def get_pickset_modal(year=CURRENT_YEAR, tid=None):
    conn = Conn()

    pickset = Pickset(psid=request.args.get("psid"))
    pickset.fill_picks(separate=False, conn=conn)       # Get pickset from DB
    pickset.fill_tournament_history(year, conn=conn)    # Get tournament history from DB

    tournament = Tournament(year=year, tid=tid)
    if tid is None:
        tournament.channel_tid = int(request.args.get("channel_tid"))
        tournament.fill_api_leaderboard()
    else:
        tournament.fill_db_rankings(conn=conn)  # Get Standings from DB

    pickset.merge_tournament(tournament)

    pickset_modal = get_template_attribute("modal.macro.html", "pickset_modal")
    return pickset_modal(pickset)


@results_mod.route("/get-player-modal")
@results_mod.route("/live/get-player-modal")
@results_mod.route("/<int:year>/<tid>/get-player-modal")
def get_player_modal(year=CURRENT_YEAR, tid=None):
    pid = int(request.args.get("pid"))
    channel_tid = request.args.get("channel_tid")

    conn = Conn()

    player = Player(pid=pid)
    player.fill_tournament_data(tid=tid, year=year, conn=conn)
    player.fill_who_picked(year=year, conn=conn)

    if tid is None:
        tournament = Tournament(year=year, channel_tid=int(channel_tid))
        tournament.fill_api_leaderboard()
        leaderboard_player = func_find(tournament.players, lambda pl: pl.id == player.id)
        player.current_tournament_data = leaderboard_player


    player_modal = get_template_attribute("modal.macro.html", "player_modal")
    return player_modal(player)
