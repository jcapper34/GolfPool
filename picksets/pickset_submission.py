from typing import List
from db.db_helper import filter_conn
from helper import CURRENT_YEAR
from picksets.pickset import Pickset
from players.player import Player
from mailer.postman import Postman

def submit_picks(name, email, pin, form_picks, send_email=True, year=CURRENT_YEAR, conn=None):
    conn = filter_conn(conn)
    # Get main levels
    picks = extract_form_picks(form_picks)

    if not validate_picks(picks, conn=conn):   # Make sure picks are valid
        return False

    psid = db_inserts(name, email, pin, picks, year, conn=conn)

    # Send Email
    if send_email:
        postman = Postman((email,))
        postman.make_picks_message(name, pin, picks)
        postman.send_message()

    return psid

def submit_change_picks(pid, name, email, pin, form_picks, conn=None):
    conn = filter_conn(conn)

    # Get main levels
    picks = extract_form_picks(form_picks)

    if not validate_picks(conn):   # Make sure picks are valid
        return False

    db_update_picks(pid, picks, conn=conn)

    # Send email
    postman = Postman((email,))
    postman.make_picks_message(name, pin, picks, update=True)
    postman.send_message()

    return True


def extract_form_picks(form_picks):
    picks = []  # Set of lists of type Player
    for level in form_picks:
        level_players = []
        for p in level:  # Iterate through form inputted players
            player_data = p.split('*')
            level_players.append(Player(name=player_data[0], id=player_data[1]))

        picks.append(level_players)

    return picks

def validate_picks(picks, year=CURRENT_YEAR, conn=None):
    if len(picks) != len(Pickset.PICKS_ALLOWED):  ## Check for correct number of levels
        return False

    for i in range(len(picks)):
        level_players = picks[i]
        if len(level_players) != Pickset.PICKS_ALLOWED[i]:
            return False

    """ Ensure that level 4 players are not in levels 1-3 """
    results = conn.exec_fetch("SELECT player_id FROM level_xref WHERE season_year=%s", (year,))
    level_pids = [x[0] for x in results]

    if any([int(p.id) in level_pids for p in picks[3]]):
        return False

    return True

""" 
Parameters: name, email, pin
Returns: participant.id
"""
INSERT_PARTICIPANT_QUERY = """
    INSERT INTO participant (name, email, pin) VALUES (%s,%s,%s)
    ON CONFLICT(name, email) DO UPDATE SET name=EXCLUDED.name, pin=EXCLUDED.pin
    RETURNING id
"""
"""
Parameters: participant_id, season_year
Returns: pickset.id
"""
INSERT_PICKSET_QUERY = """
    INSERT INTO pickset (participant_id, season_year) VALUES (%s,%s)
    RETURNING id
"""
def db_inserts(name, email, pin, picks, year=CURRENT_YEAR, conn=None):
    conn = filter_conn(conn)   # Make connection

    """ Insert participant if doesn't exist """
    results = conn.exec_fetch(INSERT_PARTICIPANT_QUERY, (name, email, pin))
    partid = results[0][0]

    """ Insert pickset """
    results = conn.exec_fetch(INSERT_PICKSET_QUERY, (partid, year))
    pid = results[0][0]

    """ Insert picks """
    db_insert_picks(pid, picks, conn=conn)

    conn.commit()   # Make sure to commit changes

    return pid

def db_insert_picks(pid, picks, conn=None):
    # Redefine Variables
    conn = filter_conn(conn)

    if isinstance(picks[0], List):  # Un-separate picks if they are separated
        picks = [pl for level_players in picks for pl in level_players]

    query = "INSERT INTO picks_xref (player_id, pickset_id) VALUES"
    for picked_player in picks:
        # Create new db player if doesn't exist
        conn.exec("INSERT INTO player (id, name) VALUES (%s, %s) ON CONFLICT DO NOTHING", (picked_player.id, picked_player.name))

        # Add to picks insert query
        s = conn.cur.mogrify(" (%s, %s),", (picked_player.id, pid)).decode("utf-8")
        query = ''.join((query, s))

    conn.exec(query[:-1])  # DB picks insert


def db_update_picks(pid, picks, conn=None):
    conn = filter_conn(conn)

    conn.exec("DELETE FROM picks_xref WHERE pickset_id=%s", (pid,))   # Delete previous picks

    db_insert_picks(pid, picks, conn=conn)  # Insert new picks

    conn.commit()