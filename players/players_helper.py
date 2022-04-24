# Puts in list of players by level


def level_separate(players):
    level_players = [[], [], [], []]
    for player in players:
        level_players[player.level-1].append(player)

    return level_players
