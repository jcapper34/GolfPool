# Library imports
from pprint import pprint
from flask import Blueprint, render_template, request, session, redirect, jsonify, url_for, get_template_attribute
from config import GOLFERS_URL, OWGR_STAT_ID, STATS_URL

# My function imports
from db.conn import Conn
from helper import CURRENT_YEAR, splash, RUNNING_LOCALLY
from mailer.postman import Postman
from picksets.pickset import Pickset
from picksets.pickset_submission import submit_change_picks, submit_picks
from picksets.picksets_db import get_all_picks, get_login, get_most_picked, get_email_pin, get_picks
from players.players_db import get_levels_db
from players.player import Player
from tournament.tournament import Tournament

mod = Blueprint("picks", __name__, template_folder='templates',
                      static_folder='static')   # Register Blueprint

HIDE_PICKS = True

""" ROUTES """

# Root of Picks Module


@mod.route("/")
def picks_index():
    return "<a href='%s'>Make Picks</a><br><a href='%s'>Change Picks</a>" % (url_for('picks.picks_make'), url_for('picks.picks_change'))


# Make Picks Page
@mod.route("/make")
def picks_make():
    if not RUNNING_LOCALLY:
        return render_template('locked-page.html', title="Make Picks")
    return render_template("make/make-picks.html", level_players=get_levels_db(CURRENT_YEAR), OWGR_URL=STATS_URL % OWGR_STAT_ID, API_PLAYERS_URL=GOLFERS_URL, year=CURRENT_YEAR)


@mod.route("/season-history")
def picks_get_season_history():
    conn = Conn()
    season_history = []
    for year in range(2015, CURRENT_YEAR):
        tournament = Tournament(year=year, tid='cumulative')
        tournament.fill_db_rankings(conn=conn)
        season_history.append(
            (year, {pl.id: pl.pos for pl in tournament.players}))

    return jsonify(season_history)


# Make Picks Submission
@mod.route("/submit", methods=['POST'])
def picks_submit():
    # Extract Form
    # Ensure name is capitalized
    name = request.form.get("name").strip().title()
    email = request.form.get("email")
    pin = request.form.get("pin")
    form_picks = [request.form.getlist("level-1"),
                  request.form.getlist("level-2"),
                  request.form.getlist("level-3"),
                  request.form.getlist("level-4")]

    try:
        # Submit pickset, will return pickset id
        psid = submit_picks(name, email, pin, form_picks)
        if not psid:  # If form not in correct format
            return "Error: Picks not submitted correctly."
    except Exception as e:   # If internal error
        print(e)
        return "Server Error: Please try again later"

    session['psid'] = psid  # Set session
    return redirect(url_for('picks.picks_confirmation'))


# Picks Confirmation Page
@mod.route("/confirmation")
def picks_confirmation():
    psid = session.get('psid')
    if psid is None:    # If no longer a session
        return redirect("index")

    # Get pickset
    pickset = Pickset(id=psid)
    pickset.picks = get_picks(psid)

    return render_template("make/picks-confirmation.html", pickset=pickset)


# Change Picks Page
@mod.route("/change")
def picks_change():
    if not RUNNING_LOCALLY:
        return render_template('locked-page.html', title="Make Picks")

    psid = session.get('psid')
    if psid is None:  # If not logged in
        return render_template('change/change-picks-login.html')

    conn = Conn()   # Will be used more than once

    # Get pickset
    pickset = Pickset(id=psid)
    pickset.picks = get_picks(psid, conn=conn)

    return render_template("change/change-picks.html",
                           level_players=get_levels_db(
                               CURRENT_YEAR, conn=conn),
                           pickset=pickset,
                           year=CURRENT_YEAR,
                           OWGR_URL=STATS_URL % 19,
                           API_PLAYERS_URL=GOLFERS_URL
                           )

# Change Picks Login
@mod.route("/change/submit-login", methods=['POST'])
def picks_change_login():
    email = request.form.get('email')
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
        return "Email does not exist"

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
        return "Your session has expired, please log back in"

    try:
        change_success = submit_change_picks(pid=f.get("psid"),
                                             name=f.get("name"),
                                             email=f.get("email"),
                                             pin=f.get("pin"),
                                             form_picks=[f.getlist('level-'+str(l)) for l in range(1, 5)])

        if not change_success:
            return "Error: Form not filled out correctly"
    except Exception as e:
        print(e)
        return "Server Error: Please try again later"

    return "Picks saved successfully, please check your email"


# Poolwide Picks Page
@mod.route("/poolwide")
@mod.route("/poolwide/<int:year>")
def picks_poolwide(year=CURRENT_YEAR):
    return render_template('poolwide/poolwide-picks.html', year=year, all_picks=get_all_picks(year))

# Most picked macro


@mod.route("/most-picked/<int:year>")
def picks_most(year=CURRENT_YEAR):
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
