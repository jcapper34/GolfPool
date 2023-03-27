from collections import defaultdict


def level_separate(players):
    """
    Puts in list of players by level
    """
    level_players = defaultdict(list)
    for player in players:
        level_players[player.level].append(player)
    
    return list(sorted(level_players.values(), key=lambda l: l[0].level))
