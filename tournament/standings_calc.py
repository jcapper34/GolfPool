from db.db_helper import filter_conn
from helper import func_find
from picksets.picksets_db import get_all_picks


def calculate_api_standings(tournament, year=None, get_picks=True, conn=None):
    conn = filter_conn(conn)

    year = year if year is not None else tournament.year

    if get_picks:
        tournament.picksets = get_all_picks(
            year, conn=conn)  # Load DB Picks

    for pickset in tournament.picksets:
        if pickset.points is None:
            pickset.points = 0
        for picked_player in pickset.picks:
            match = func_find(
                tournament.players, func=lambda x: x.id == picked_player.id)
            if match is not None:
                pickset.points += match.points
                picked_player.merge(match)

    tournament.picksets.sort(key=lambda x: x.points,
                             reverse=True)    # Sort Standings

    tournament.picksets = rank(tournament.picksets)


def rank(picksets):  # Give Picksets their positions after calculating standings
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
