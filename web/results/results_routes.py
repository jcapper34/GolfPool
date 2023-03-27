from dataclasses import asdict
from http import HTTPStatus
import math
import os
import uuid

from flask import Blueprint, get_template_attribute, jsonify, redirect, render_template, request, session, url_for
from config import LIVE_TOURNAMENT_OVERRIDE_ID, LIVE_TOURNAMENT_OVERRIDE_YEAR, PICKS_LOCKED, XL_DIR, TOURNAMENT_NAME_MAP, UNLOCK_ALL_PAGES

from helper.globalcache import GlobalCache
from helper.helpers import func_find, CURRENT_YEAR, resolve_photo
from picksets.pickset import Pickset
from picksets.pickset_getters import get_all_picks, get_picks, get_tournament_history
from players.player import Player
from players.player_getters import get_player_photo, get_tournament_player_db, who_picked_player
from tournament.tournament_calculations import calculate_standings
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
    # Block if picks are not locked yet
    if not PICKS_LOCKED and not UNLOCK_ALL_PAGES:
        if request.args.get('main_section_only') is None:
            return render_template("standings-not-found.html", past_events=get_past_events()), HTTPStatus.NOT_FOUND
        else:
            return "<p class='has-text-centered'>No results to show</p>"  
    
    # Override live tournament if applicable
    # Otherwise try to get tournament metadata from cache
    if LIVE_TOURNAMENT_OVERRIDE_ID is not None and LIVE_TOURNAMENT_OVERRIDE_YEAR is not None:
        channel_tid = LIVE_TOURNAMENT_OVERRIDE_ID
        year = LIVE_TOURNAMENT_OVERRIDE_YEAR
    elif GlobalCache.live_tournament is not None:
        channel_tid = GlobalCache.live_tournament.tid
        year = GlobalCache.live_tournament.year
    else:
        raise RuntimeError

    tournament = get_api_tournament(channel_tid=channel_tid, year=year)
    tournament.picksets = calculate_standings(tournament.players, get_all_picks(year))
    tournament.year = year

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

@mod.route("/<int:year>")
@mod.route("/<int:year>/<tid>")
def results_past(year, tid=None):
    # Get Database Rankings
    if tid is None or tid.casefold() == 'cumulative':
        tournament_name = "Cumulative"
        tid = "cumulative"
    elif tid in TOURNAMENT_NAME_MAP:
        tournament_name = TOURNAMENT_NAME_MAP[tid]
    else:
        return "Tournament not found", HTTPStatus.BAD_REQUEST
    
    tournament = Tournament(name=tournament_name, year=year, tid=tid)
    tournament.players = get_db_rankings(tid, year)
    
    past_events = get_past_events()
    
    # If tournament not found in DB
    if tournament.players is None:
        if request.args.get('main_section_only') is None:
            return render_template("standings-not-found.html", past_events=past_events), HTTPStatus.NOT_FOUND
        else:
            return "<p class='has-text-centered'>No results to show</p>"

    tournament.picksets = get_db_standings(tid, year)

    # Merge all picks with tournament
    all_picks = get_all_picks(year)
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

    pickset = Pickset(psid)
    pickset.picks = get_picks(psid, separate=False)

    # Get tournament history from DB
    pickset.tournament_history = get_tournament_history(psid)

    tournament = None
    if tid is None:
        tournament = get_api_tournament(channel_tid)
        pickset.merge_tournament(tournament)

    else:
        tournament_name = TOURNAMENT_NAME_MAP[tid] if tid != 'cumulative' else "Cumulative"
        tournament = Tournament(name=tournament_name, year=year, tid=tid)
        tournament.players = get_db_rankings(tid, year)  # Get Standings from DB
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
    pid = request.args.get("pid")
    channel_tid = request.args.get("channel_tid")

    player = Player(id=pid)
    player.picked_by = who_picked_player(player.id, year=year)
    
    # Get API results
    if tid is None:
        tournament = get_api_tournament(channel_tid)
        leaderboard_player = func_find(
            tournament.players, lambda pl: pl.id == player.id)
        player.merge_attributes(asdict(leaderboard_player))
        player.status = leaderboard_player.status
        player.scorecards = func_find(
            tournament.scorecards, lambda sc: sc['golferId'] == player.id, limit=4)
        
        # See if photo is available from DB
        photo = get_player_photo(pid)
        player.photo_url = photo if photo is not None else player.photo_url
    # Get DB Results
    else:
        tournament_results = get_tournament_player_db(
            pid, year)
        player.season_history = tournament_results
        player.photo_url = resolve_photo(tournament_results[0]['photo_url'], tournament_results[0]['tour_id'])
        if tid != "cumulative":
            current_results = func_find(tournament_results, lambda t: t['tid'] == tid)
            if current_results is None:
                return "Invalid tournament id was specified" # TODO: Return error
            current_results = dict(current_results)
            del current_results['tid']
            del current_results['tour_id']
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