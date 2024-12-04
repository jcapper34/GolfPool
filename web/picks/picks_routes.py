# Library imports
from flask import Blueprint, render_template, request, session, redirect, jsonify, url_for, get_template_attribute
from http import HTTPStatus
from config import *

# My function imports
from helpers import CURRENT_YEAR, request_json
from mailer.postman import Postman
from picksets.pickset_submission import submit_change_picks, submit_picks
from picksets.pickset_getters import get_all_picks, get_login, get_most_picked, get_email_pin, get_picks, get_pickset
from players.player_getters import get_non_leveled_players, get_level_limits, get_levels_db
from tournament.tournament_retriever import get_db_rankings, get_past_events

mod = Blueprint("picks", __name__, 
                template_folder='templates',
                static_folder='static')   # Register Blueprint

""" ROUTES """

@mod.route("/")
def picks_index():
    """
    Root of Picks Module
    """
    return "<a href='%s'>Make Picks</a><br><a href='%s'>Change Picks</a>" % (url_for('picks.picks_make'), url_for('picks.picks_change'))


@mod.route("/make")
def picks_make():
    """
    Make Picks Page
    """
    # Make sure you don't allow picks to be made if picks are locked
    if not UNLOCK_ALL_PAGES and PICKS_LOCKED:
        return render_template('locked-page.html', title="Make Picks"), HTTPStatus.FORBIDDEN
    
    return render_template("make/make-picks.html", 
                           level_players=get_levels_db(CURRENT_YEAR),
                           level_limits = get_level_limits(CURRENT_YEAR),
                           OWGR_URL=OWGR_RANKINGS_URL % (OWGR_PAGE_SIZE_MAKE_PICKS, 1), 
                           year=CURRENT_YEAR)


@mod.route("/season-history")
def picks_get_season_history():
    season_history = []
    for year in get_past_events():
        players = get_db_rankings(tid='cumulative', year=year)
        season_history.append(
            (year, {pl.id: pl.pos for pl in players}))

    return jsonify(season_history)


@mod.route("/final-level-suggestions/<int:year>", methods=['GET'])
def picks_get_final_level_suggestions(year):
    ranked_players = [
        {
            "id": str(pl["player"]["id"]),
            "name": pl["player"]["fullName"]
        }
        for pl in request_json(OWGR_RANKINGS_URL % (OWGR_PAGE_SIZE_MAKE_PICKS, 1))["rankingsList"]
    ]

    players_to_add = filter(lambda player: player["id"] not in {p["id"] for p in ranked_players}, 
                            get_non_leveled_players(year))

    return jsonify(ranked_players + list(players_to_add))


@mod.route("/submit", methods=['POST'])
def picks_submit():
    """
    Make Picks Submission
    """
    # Extract Form
    # Ensure name is capitalized
    name = request.form.get("name").strip().title()
    email = request.form.get("email").casefold()
    pin = request.form.get("pin")
    form_picks = [request.form.getlist("level-1"),
                  request.form.getlist("level-2"),
                  request.form.getlist("level-3"),
                  request.form.getlist("level-4")]

    try:
        # Submit pickset, will return pickset id
        psid = submit_picks(name, email, pin, form_picks)
        if not psid:  # If form not in correct format
            return "Error: Picks not submitted correctly.", HTTPStatus.BAD_REQUEST
    except Exception as e:   # If internal error
        print(e)
        return "Server Error: Please try again later", HTTPStatus.INTERNAL_SERVER_ERROR

    session['psid'] = psid  # Set session
    return redirect(url_for('picks.picks_confirmation'))


# Picks Confirmation Page
@mod.route("/confirmation")
def picks_confirmation():
    psid = session.get('psid')
    if psid is None:    # If no longer a session
        return redirect("index")

    # Get pickset
    pickset = get_pickset(psid)
    pickset.picks = get_picks(psid)

    return render_template("make/picks-confirmation.html", pickset=pickset)


# Change Picks Page
@mod.route("/change")
def picks_change():
    # Make sure you don't allow pick changes if picks are locked
    if not UNLOCK_ALL_PAGES and PICKS_LOCKED:
        return render_template('locked-page.html', title="Change Picks"), HTTPStatus.FORBIDDEN

    psid = session.get('psid')
    if psid is None:  # If not logged in
        return render_template('change/change-picks-login.html')

    # Get pickset
    pickset = get_pickset(psid)

    # Pickset not found means it has been deleted. Thus, log out
    if pickset is None:
        return redirect(url_for("picks.picks_change_logout"), code=HTTPStatus.NOT_FOUND.value)

    pickset.picks = get_picks(psid)
    return render_template("change/change-picks.html",
                            level_players=get_levels_db(
                                CURRENT_YEAR),
                            level_limits=get_level_limits(CURRENT_YEAR),
                            pickset=pickset,
                            year=CURRENT_YEAR,
                            OWGR_URL=OWGR_RANKINGS_URL % (OWGR_PAGE_SIZE_MAKE_PICKS, 1))

# Change Picks Login
@mod.route("/change/submit-login", methods=['POST'])
def picks_change_login():
    # Make sure you don't allow changes if picks are locked
    if not UNLOCK_ALL_PAGES and PICKS_LOCKED:
        return render_template('locked-page.html', title="Change Picks"), HTTPStatus.FORBIDDEN
    email = request.form.get('email').casefold()
    pin = request.form.get('pin')
    psid = get_login(email, pin)
    resp = {"success": True}

    if not psid:
        resp['success'] = False
    else:
        session['psid'] = psid

    return jsonify(resp)


@mod.route("/change/forgot-pin", methods=['GET', 'POST'])
def picks_forgot_pin():
    if request.method == 'GET':
        return render_template('change/change-picks-forgot-pin.html', username=request.args.get("username"))

    email = request.form.get('email')
    pin = get_email_pin(email)
    if pin is None:
        return "Email does not exist", HTTPStatus.NOT_FOUND

    postman = Postman(recipients=(email,))
    postman.message_subject += " | Your PIN"
    postman.message_body = "The PIN for %s is %s\n\n" % (email, pin[0])

    postman.send_message()

    return "Your PIN has been sent to your email"


# Change Picks Logout
@mod.route("/change/logout")
def picks_change_logout():
    if session.get('psid') is not None:  # If logged in
        session.clear()

    return redirect(url_for('picks.picks_change'))


# Change Picks Submission
@mod.route("/submit-changes", methods=['POST'])
def picks_submit_changes():
    f = request.form

    if session.get("psid") != int(f.get("psid")):
        return "Your session has expired, please log back in", 440 # Code for Login Timeout (not in HttpStatus module)

    try:
        change_success = submit_change_picks(pid=f.get("psid"),
                                             name=f.get("name"),
                                             email=f.get("email").casefold(),
                                             pin=f.get("pin"),
                                             form_picks=[f.getlist('level-'+str(l)) for l in range(1, 5)])

        if not change_success:
            return "Error: Form not filled out correctly", HTTPStatus.BAD_REQUEST
    except Exception as e:
        print(e)
        return "Server Error: Please try again later", HTTPStatus.INTERNAL_SERVER_ERROR

    return "Picks saved successfully, please check your email"


# Poolwide Picks Page
@mod.route("/poolwide")
@mod.route("/poolwide/<int:year>")
def picks_poolwide(year=CURRENT_YEAR):
    # Make sure you don't show current year picks if picks aren't locked
    if not UNLOCK_ALL_PAGES:
        if not PICKS_LOCKED and year == CURRENT_YEAR:
            year = CURRENT_YEAR - 1
    
    return render_template('poolwide/poolwide-picks.html', year=year, all_picks=get_all_picks(year), level_limits=get_level_limits(year))

# Most picked macro
@mod.route("/most-picked/<int:year>")
def picks_most(year=CURRENT_YEAR):
    # Make sure you don't show current year picks if picks aren't locked
    if not UNLOCK_ALL_PAGES:
        if not PICKS_LOCKED and year == CURRENT_YEAR:
            year = CURRENT_YEAR - 1
    most_picked_macro = get_template_attribute(
        "poolwide/poolwide-picks.macro.html", "most_picked_tab")
    return most_picked_macro(get_most_picked(year))


# # Pickset Page
# @picks_mod.route("/<int:psid>")
# def pickset_page(psid):
#     pickset = Pickset(id=psid)
#     pickset.fill_picks()
#
#     return render_template("pickset-page.html", pickset=pickset)
