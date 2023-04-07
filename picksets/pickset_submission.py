from http import HTTPStatus
from typing import List

import psycopg2
from appexceptions import ConflictingPicksetException
from helper.helpers import CURRENT_YEAR
from picksets.pickset import Pickset
from players.player import Player
from mailer.postman import Postman
from db.connection_pool import db_pool
from players.player_getters import get_level_limits


def submit_picks(name, email, pin, form_picks, send_email=True, year=CURRENT_YEAR) -> bool:
    # Get main levels
    picks = extract_form_picks(form_picks)

    if not validate_picks(picks):   # Make sure picks are valid
        return False

    psid = db_inserts(name, email, pin, picks, year)

    # Send Email
    if send_email:
        postman = Postman((email,))
        postman.make_picks_message(name, pin, picks)
        postman.send_message()

    return psid


def submit_change_picks(pid, name, email, pin, form_picks) -> bool:

    # Get main levels
    picks = extract_form_picks(form_picks)

    if not validate_picks(picks):   # Make sure picks are valid
        return False

    db_update_picks(pid, picks)

    # Send email
    postman = Postman((email,))
    postman.make_picks_message(name, pin, picks, update=True)
    postman.send_message()

    return True


def extract_form_picks(form_picks) -> List:
    picks = []  # Set of lists of type Player
    for level in form_picks:
        level_players = []
        for p in level:  # Iterate through form inputted players
            player_data = p.split('*')
            level_players.append(
                Player(name=player_data[0], id=player_data[1]))

        picks.append(level_players)

    return picks


def validate_picks(picks, year=CURRENT_YEAR) -> bool:
    level_limits = get_level_limits(year)
    num_levels = len(level_limits)
    if len(picks) != num_levels:  # Check for correct number of levels
        return False

    for i in range(len(picks)):
        level_players = picks[i]
        if len(level_players) != level_limits[i]:
            return False

    """ Ensure that level 4 players are not in levels 1-3 """
    results = None
    with db_pool.get_conn() as conn:
        results = conn.exec_fetch(
            "SELECT player_id FROM level_xref WHERE season_year=%s", (year,))

    level_pids = [x[0] for x in results]

    if any([int(p.id) in level_pids for p in picks[-1]]):
        return False

    return True


def db_inserts(name, email, pin, picks, year=CURRENT_YEAR) -> int:
    """ 
    Parameters: name, email
    Returns: participant.id
    """
    INSERT_PARTICIPANT_QUERY = """
        INSERT INTO participant (name, email) VALUES (%s,%s)
        ON CONFLICT(name, email) DO UPDATE SET name=EXCLUDED.name
        RETURNING id
    """
    """
    Parameters: participant_id, season_year, pin
    Returns: pickset.id
    """
    INSERT_PICKSET_QUERY = """
        INSERT INTO pickset (participant_id, season_year, pin) VALUES (%s,%s,%s)
        RETURNING id
    """
    psid = None
    with db_pool.get_conn() as conn:
        """ Insert participant if doesn't exist """
        results = conn.exec_fetch(INSERT_PARTICIPANT_QUERY, (name, email))
        partid = results[0][0]

        """ Insert pickset """
        try:
            results = conn.exec_fetch(INSERT_PICKSET_QUERY, (partid, year, pin))
        except psycopg2.errors.UniqueViolation:
            raise ConflictingPicksetException("Pickset with that name and email already exists for this season. You may have accidentally sent multiple submissions") 

        """ Insert picks """
        psid = results[0][0]
        db_insert_picks(psid, picks, conn=conn)

        conn.commit()   # Make sure to commit changes

    return psid


def db_insert_picks(psid, picks, conn) -> None:
    '''
    The connection should already be wrapped using a "with" statement before this function is called
    '''
    if isinstance(picks[0], List):  # Un-separate picks if they are separated
        picks = [pl for level_players in picks for pl in level_players]

    query = "INSERT INTO picks_xref (player_id, pickset_id) VALUES"
    for picked_player in picks:
        # Create new db player if doesn't exist
        conn.exec("INSERT INTO player (id, name) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                  (picked_player.id, picked_player.name))

        # Add to picks insert query
        s = conn.cur.mogrify(
            " (%s, %s),", (picked_player.id, psid)).decode("utf-8")
        query = ''.join((query, s))

    conn.exec(query[:-1])  # DB picks insert


def db_update_picks(pid, picks) -> None:
    with db_pool.get_conn() as conn:
        conn.exec("DELETE FROM picks_xref WHERE pickset_id=%s",
                (pid,))   # Delete previous picks

        db_insert_picks(pid, picks, conn=conn)  # Insert new picks

        conn.commit()
