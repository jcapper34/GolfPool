from typing import List
from helpers import func_find
from picksets.pickset import Pickset
from players.player import Player


def calculate_standings(players: List[Player], picksets: List[Pickset]) -> List[Pickset]:
    '''
    Calculate the pickset standings from the players
    
    '''
    # Caches the points of players
    player_points_map = {}
    for pickset in picksets:
        if pickset.points is None:
            pickset.points = 0
        for picked_player in pickset.picks:
            if picked_player.id in player_points_map:
                pickset.points += player_points_map[picked_player.id]
            else:
                match = func_find(
                    players, func=lambda x: x.id == picked_player.id)
                points = match.points if match is not None else 0

                pickset.points += points
                player_points_map[picked_player.id] = points
    
    picksets.sort(key=lambda x: x.points,
                             reverse=True)    # Sort Standings

    return rank(picksets)


def rank(picksets: List[Pickset]) -> List[Pickset]: 
    '''
    Give Picksets their positions after calculating standings
    
    '''
    n = len(picksets)
    pos = 1
    for i in range(n):
        points = picksets[i].points
        tie = False
        if i == 0 and n > 1 and points == picksets[i + 1].points:
            tie = True
        elif points == picksets[i - 1].points:
            tie = True
        if not tie:
            pos = i + 1

        picksets[i].pos = pos

    return picksets
