from typing import List
from db.database_connection import DatabaseConnection
from helpers import CURRENT_YEAR
import logger
from picksets.pickset import Pickset
from players.player import Player
from mailer.postman import Postman
from db.connection_pool import db_pool
from players.player_getters import get_level_limits
import pyodbc


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
    with DatabaseConnection() as conn:
        cursor = conn.cursor()
        results = cursor.execute(
            "SELECT player_id FROM level_xref WHERE season_year=?", year).fetchall()
    
    level_pids = [x[0] for x in results]

    if any(p.id in level_pids for p in picks[-1]):
        return False

    return True


def db_inserts(name, email, pin, picks, year=CURRENT_YEAR) -> int:
    """ 
    Parameters: name, email
    Returns: participant.id
    """
    INSERT_PARTICIPANT_QUERY = """
        INSERT INTO participant (name, email) 
            OUTPUT Inserted.id
            VALUES (?,?)
    """
    """ 
    Parameters: name, email
    Returns: participant.id
    """
    GET_PARTICIPANT_ID_QUERY = """
        SELECT id FROM participant WHERE name = ? AND email = ?
    """
    """
    Parameters: participant_id, season_year, pin
    Returns: pickset.id
    """
    INSERT_PICKSET_QUERY = """
        INSERT INTO pickset (participant_id, season_year, pin) 
            OUTPUT Inserted.id
            VALUES (?,?,?)
    """
    psid = None
    with DatabaseConnection() as conn:
        cursor = conn.cursor()

        """ Insert participant if doesn't exist """
        logger.info("Inserting participant (%s, %s) into database", name, email)
        participant_id = None
        try:
            results = cursor.execute(INSERT_PARTICIPANT_QUERY, (name, email)).fetchone()
            participant_id = results[0]
        except pyodbc.IntegrityError:
            logger.info("Participant (%s, %s) already existed in database", name, email)
            results = cursor.execute(GET_PARTICIPANT_ID_QUERY, (name, email)).fetchone()
            participant_id = results[0]

        """ Insert pickset """
        logger.info("Inserting pickset for participant id=%d", participant_id)
        results = cursor.execute(INSERT_PICKSET_QUERY, (participant_id, year, pin)).fetchone()
        psid = results[0]
        logger.info("New pickset was created with id=%d", psid)

        """ Insert picks """
        db_insert_picks(psid, picks, cursor)

        cursor.commit()   # Make sure to commit changes

    return psid


def db_insert_picks(psid, picks, cursor) -> None:
    '''
    The connection should already be wrapped using a "with" statement before this function is called
    '''
    if isinstance(picks[0], List):  # Un-separate picks if they are separated
        picks = [pl for level_players in picks for pl in level_players]

    # Create new db player if doesn't exist
    logger.info("Inserting picked players into database if they don't exist")
    for picked_player in picks:
        try:
            cursor.execute("INSERT INTO player (id, name) VALUES (?, ?)",
                  (picked_player.id, picked_player.name))
        except pyodbc.IntegrityError:
            pass

    logger.info("Inserting picks into database for pickset %d", psid)
    cursor.enable_fastexecutemany()
    cursor.executemany("INSERT INTO picks_xref (player_id, pickset_id) VALUES (?,?)", 
                       ((p.id, psid) for p in picks))
    logger.info("Successfully inserted picks into database for pickset %d", psid)


def db_update_picks(pid, picks) -> None:
    with DatabaseConnection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM picks_xref WHERE pickset_id=?", pid)   # Delete previous picks

        db_insert_picks(pid, picks, cursor)  # Insert new picks

        cursor.commit()
