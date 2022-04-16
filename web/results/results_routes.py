from dataclasses import asdict
import json
import math
import os
import uuid

from flask import Blueprint, render_template, request, get_template_attribute, jsonify, session, Response, redirect, url_for
from config import PICKS_LOCKED, XL_DIR, TOURNAMENT_NAME_MAP

from db.conn import Conn
from helper import func_find, CURRENT_YEAR
from picksets.pickset import Pickset
from picksets.pickset_getters import get_all_picks, get_picks, get_tournament_history
from players.player import Player
from players.player_getters import get_tournament_player_db, who_picked_player
from tournament.tournament_calculations import calculate_api_standings
from tournament.tournament import Tournament
from tournament.tournament_retriever import get_api_tournament, get_db_rankings, get_db_standings, get_past_events
from tournament.xl_generator import write_picks_workbook

mod = Blueprint("results", __name__, template_folder='templates',
                static_folder='static')   # Register blueprint

""" LIVE ROUTES """

# Root of Results Module


@mod.route("/")
def results_home():
    return redirect(url_for('results.results_live'))
    
@mod.route("/live")
def results_live():
    year = CURRENT_YEAR if PICKS_LOCKED else CURRENT_YEAR - 1    
    tournament = get_api_tournament()
    calculate_api_standings(tournament, year=year)

    if request.args.get("refresh") is not None:    # If refresh
        standings_macro = get_template_attribute(
            "standings.macro.html", "standings_table")
        leaderboard_macro = get_template_attribute(
            "standings.macro.html", "leaderboard_table")
        return jsonify([standings_macro(tournament.picksets), leaderboard_macro(tournament.players)])

    if request.args.get('main_section_only') is not None:
        main_section_macro = get_template_attribute(
            "standings.macro.html", "standings_main_section")
        return main_section_macro(tournament, user_psid=session.get("psid"), add_refresh=True, add_export=False)

    return render_template('standings-live.html', tournament=tournament, past_events=get_past_events(), user_psid=session.get("psid"))


""" PAST ROUTES """

# Past Standings


@mod.route("/<int:year>/<tid>")
def results_past(year, tid):
    conn = Conn()

    past_events = get_past_events()

    # Get Database Rankings
    tournament_name = TOURNAMENT_NAME_MAP[tid] if tid != 'cumulative' else "Cumulative"
    tournament = Tournament(name=tournament_name, year=year, tid=tid)
    tournament.players = get_db_rankings(tid, year, conn=conn)
    
    # If tournament not found in DB
    if tournament.players is None:
        if request.args.get('main_section_only') is None:
            return render_template("locked-standings.html", tournament=tournament, past_events=past_events)
        else:
            return "<p class='has-text-centered'>No results to show</p>"

    tournament.picksets = get_db_standings(tid, year, conn=conn)

    # Merge all picks with tournament
    all_picks = get_all_picks(year, conn=conn)
    tournament.merge_all_picks(all_picks)

    if request.args.get('main_section_only') is not None:   # For quick tab switching
        main_section_macro = get_template_attribute(
            "standings.macro.html", "standings_main_section")
        return main_section_macro(tournament, user_psid=session.get("psid"), add_refresh=False, add_export=True)

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

    tournament = None
    if tid is None:
        tournament = get_api_tournament()
        pickset.merge_tournament(tournament)

    else:
        tournament_name = TOURNAMENT_NAME_MAP[tid] if tid != 'cumulative' else "Cumulative"
        tournament = Tournament(name=tournament_name, year=year, tid=tid)
        tournament.players = get_db_rankings(tid, year, conn=conn)  # Get Standings from DB
        pickset.merge_tournament(tournament)

    for pick in pickset.picks:
        if pick.pos is None:
            pick.raw_pos = math.inf
        else:
            pick.raw_pos = int(pick.pos) if isinstance(pick.pos, int) or pick.pos[0] != 'T' else int(pick.pos[1:])
    
    pickset.picks.sort(key=lambda p: (p.raw_pos, p.status))
    
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

    # Get API results
    if tid is None:
        tournament = get_api_tournament(channel_tid)
        # tournament.year = year
        leaderboard_player = func_find(
            tournament.players, lambda pl: pl.id == player.id)
        player.merge_attributes(asdict(leaderboard_player))
        player.status = leaderboard_player.status
        player.scorecards = func_find(
            tournament.scorecards, lambda sc: sc['golferId'] == player.id, limit=4)
    # Get DB Results
    else:
        tournament_results = get_tournament_player_db(
            pid, year, conn=conn)
        player.season_history = tournament_results
        player.photo_url = tournament_results[0]['photo_url']
        if tid != "cumulative":
            current_results = func_find(tournament_results, lambda t: t['tid'] == tid)
            if current_results is None:
                return "Invalid tournament id was specified" # TODO: Return error
            current_results = dict(current_results)
            del current_results['tid']
            player.merge_attributes(current_results)

    player_modal = get_template_attribute("modal.macro.html", "player_modal")
    return player_modal(player)


@mod.route("/<int:year>/<tid>/generate-xl")
def excel_generation_request(year, tid):
    folder_name = os.path.join(XL_DIR, str(uuid.uuid4()))
    if not os.path.exists(folder_name):
        os.makedirs(folder_name, exist_ok=True)
    
    tournament_name = TOURNAMENT_NAME_MAP.get(tid, "Cumulative")
    if tid == 'cumulative':
        tid_list = list(TOURNAMENT_NAME_MAP.items())
    else:
        tid_list = [(tid, tournament_name)]
    
    filepath = os.path.join(folder_name, tournament_name + ".xlsx")
    
    write_picks_workbook(tid_list, year, filepath)

    url_out = "/" + "/".join(filepath.split('/')[1:])
    return redirect(url_out)