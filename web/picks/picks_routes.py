# Library imports
from flask import Blueprint, render_template, request, session, redirect, jsonify, url_for, get_template_attribute
from config import GOLFERS_URL, OWGR_STAT_ID, PICKS_LOCKED, STATS_URL, UNLOCK_ALL_PAGES

# My function imports
from db.connection import Conn
from helper.helpers import CURRENT_YEAR
from mailer.postman import Postman
from picksets.pickset_submission import submit_change_picks, submit_picks
from picksets.pickset_getters import get_all_picks, get_login, get_most_picked, get_email_pin, get_picks, get_pickset
from players.player_getters import get_levels_db
from tournament.tournament_retriever import get_db_rankings, get_past_events

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
    # Make sure you don't allow picks to be made if picks are locked
    if not UNLOCK_ALL_PAGES and PICKS_LOCKED:
        return render_template('locked-page.html', title="Make Picks")
    return render_template("make/make-picks.html", level_players=get_levels_db(CURRENT_YEAR), OWGR_URL=STATS_URL % (OWGR_STAT_ID, CURRENT_YEAR), API_PLAYERS_URL=GOLFERS_URL, year=CURRENT_YEAR)


@mod.route("/season-history")
def picks_get_season_history():
    season_history = []
    for year in get_past_events():
        players = get_db_rankings(tid='cumulative', year=year)
        season_history.append(
            (year, {pl.id: pl.pos for pl in players}))

    return jsonify(season_history)


# Make Picks Submission
@mod.route("/submit", methods=['POST'])
def picks_submit():
    # Extract Form
    # Ensure name is capitalized
    name = request.form.get("name").strip().title()
    email = request.form.get("email").lower()
    pin = request.form.get("pin")
    form_picks = [request.form.getlist("level-1"),
                  request.form.getlist("level-2"),
                  request.form.getlist("level-3"),
                  request.form.getlist("level-4")]

    try:
        # Submit pickset, will return pickset id
        psid = submit_picks(name, email, pin, form_picks)
        if not psid:  # If form not in correct format
            return "Error: Picks not submitted correctly.", 500
    except Exception as e:   # If internal error
        print(e)
        return "Server Error: Please try again later", 500

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
        return render_template('locked-page.html', title="Change Picks")

    psid = session.get('psid')
    if psid is None:  # If not logged in
        return render_template('change/change-picks-login.html')

    # Get pickset
    pickset = get_pickset(psid)
    pickset.picks = get_picks(psid)

    return render_template("change/change-picks.html",
                           level_players=get_levels_db(
                               CURRENT_YEAR),
                           pickset=pickset,
                           year=CURRENT_YEAR,
                           OWGR_URL=STATS_URL % (19, CURRENT_YEAR),
                           API_PLAYERS_URL=GOLFERS_URL
                           )

# Change Picks Login
@mod.route("/change/submit-login", methods=['POST'])
def picks_change_login():
    # Make sure you don't allow changes if picks are locked
    if not UNLOCK_ALL_PAGES and PICKS_LOCKED:
        return render_template('locked-page.html', title="Change Picks")
    email = request.form.get('email').lower()
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
                                             email=f.get("email").lower(),
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
    # Make sure you don't show current year picks if picks aren't locked
    if not UNLOCK_ALL_PAGES:
        if not PICKS_LOCKED and year == CURRENT_YEAR:
            year = CURRENT_YEAR - 1
    
    return render_template('poolwide/poolwide-picks.html', year=year, all_picks=get_all_picks(year))

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
