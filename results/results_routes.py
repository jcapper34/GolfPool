import json

from flask import Blueprint, render_template, request, get_template_attribute, jsonify, session, Response

from db.conn import Conn
from helper import func_find, CURRENT_YEAR, RUNNING_LOCALLY
from picksets.pickset import Pickset
from picksets.pickset_getters import get_all_picks, get_picks, get_tournament_history
from players.player import Player
from players.player_getters import get_tournament_player_db, who_picked_player
from tournament.tournament_calculations import calculate_api_standings
from tournament.tournament import Tournament
from tournament.tournament_retriever import get_api_tournament

mod = Blueprint("results", __name__, template_folder='templates',
                        static_folder='static')   # Register blueprint

""" LIVE ROUTES """

# Root of Results Module

@mod.route("/")
@mod.route("/live")
def results_live():
    # if not RUNNING_LOCALLY:
    #     return render_template('locked-page.html', title="Make Picks")

    tournament = get_api_tournament()
    calculate_api_standings(tournament, year=CURRENT_YEAR)

    if request.args.get("refresh") is not None:    # If refresh
        standings_macro = get_template_attribute(
            "standings.macro.html", "standings_table")
        leaderboard_macro = get_template_attribute(
            "standings.macro.html", "leaderboard_table")
        return jsonify([standings_macro(tournament.picksets), leaderboard_macro(tournament.players)])

    if request.args.get('main_section_only') is not None:
        main_section_macro = get_template_attribute(
            "standings.macro.html", "standings_main_section")
        return main_section_macro(tournament, user_psid=session.get("psid"), add_refresh=True)

    return render_template('standings-live.html', tournament=tournament, past_events=Tournament.get_past_events(), user_psid=session.get("psid"))


""" PAST ROUTES """

# Past Standings


@mod.route("/<int:year>/<tid>")
def results_past(year, tid):
    conn = Conn()

    past_events = Tournament.get_past_events()

    # Get Database Standings
    tournament = Tournament(year=year, tid=tid)
    # If tournament not found in DB
    if not tournament.fill_db_rankings(conn=conn):
        if request.args.get('main_section_only') is None:
            return render_template("locked-standings.html", tournament=tournament, past_events=past_events)
        else:
            return "<p class='has-text-centered'>No results to show</p>"

    tournament.fill_db_standings(conn=conn)

    # Merge all picks with tournament
    all_picks = get_all_picks(year, conn=conn)
    tournament.merge_all_picks(all_picks)

    if request.args.get('main_section_only') is not None:   # For quick tab switching
        main_section_macro = get_template_attribute(
            "standings.macro.html", "standings_main_section")
        return main_section_macro(tournament, user_psid=session.get("psid"))

    return render_template('standings-past.html', tournament=tournament, past_events=past_events, user_psid=session.get("psid"))


# Past Standings Pickset Modal
@mod.route("/get-pickset-modal")
@mod.route("/live/get-pickset-modal")
@mod.route("/<int:year>/<tid>/get-pickset-modal")
def get_pickset_modal(year=CURRENT_YEAR, tid=None):
    psid = request.args.get("psid")
    channel_tid = request.args.get("channel_tid")

    conn = Conn()

    pickset = Pickset(psid)
    pickset.picks = get_picks(psid, separate=False, conn=conn)

    # Get tournament history from DB
    pickset.tournament_history = get_tournament_history(psid, conn=conn)

    tournament = Tournament(year=year, tid=tid)
    if tid is None:
        tournament = get_api_tournament()
        pickset.merge_tournament(tournament)

    else:
        tournament.fill_db_rankings(conn=conn)  # Get Standings from DB
        pickset.merge_tournament(tournament)
        for pick in pickset.picks:
            pick.raw_pos = pick.pos

    for pick in pickset.picks:
        if pick.raw_pos is None:
            pick.raw_pos = 9999

    pickset_modal = get_template_attribute("modal.macro.html", "pickset_modal")
    return pickset_modal(pickset)


@mod.route("/get-player-modal")
@mod.route("/live/get-player-modal")
@mod.route("/<int:year>/<tid>/get-player-modal")
def get_player_modal(year=CURRENT_YEAR, tid=None):
    pid = int(request.args.get("pid"))
    channel_tid = request.args.get("channel_tid")

    conn = Conn()

    player = Player(id=pid)
    player.picked_by = who_picked_player(player.id, year=year, conn=conn)

    if tid is None:
        tournament = get_api_tournament(channel_tid=int(channel_tid))
        tournament.year = year
        leaderboard_player = func_find(
            tournament.players, lambda pl: pl.id == player.id)

        player.photo_url = leaderboard_player.photo_url
        player.current_tournament_data = leaderboard_player
        player.scorecards = func_find(
            tournament.scorecards, lambda sc: sc['golferId'] == player.id, limit=4)
    else:
        player.merge(get_tournament_player_db(pid, tid, year, conn=conn))

    player_modal = get_template_attribute("modal.macro.html", "player_modal")
    return player_modal(player)
