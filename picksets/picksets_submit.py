from picksets.pickset import Pickset
from players.player import Player
from helper import CURRENT_YEAR

def submit_picks(name, email, pin, level_1, level_2, level_3, level_4):
    # Get main levels
    main_levels = []    # List of lists of type Player
    for level in (level_1, level_2, level_3):
        level_players = []
        for p in level:   # Iterate through form inputted players
            player_data = p.split("*")
            level_players.append(Player(name=player_data[0], pid=player_data[1]))

        main_levels.append(level_players)

    return Pickset(
        psid='1',
        name=name,
        email=email,
        pin=pin,
        picks=main_levels
    )

class FormSubmissionIncompleteError(Exception):
    pass

def validate_picks():
    pass


def insert_picks():
    pass