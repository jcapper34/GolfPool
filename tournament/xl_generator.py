from db.connection import Conn
from helpers import func_find
from picksets.pickset_getters import get_all_picks
import xlsxwriter as xlsx

from tournament.tournament import Tournament
from tournament.tournament_retriever import get_db_rankings, get_db_standings


def write_picks_worksheet(workbook, ws_name, tid, year, picksets, conn=None) -> None:
    bold_center_format = workbook.add_format({'align': 'center', "bold": True})
    italic_format = workbook.add_format({'italic': True})
    points_cell_format = workbook.add_format({'align': 'left'})

    worksheet = workbook.add_worksheet(ws_name)

    tournament = Tournament(year=year, tid=tid)
    tournament.players = get_db_rankings(tid, year)
    tournament.picksets = get_db_standings(tid, year)
    
    # Don't generate if standings don't exist
    if tournament.players is None or tournament.picksets is None:
        return
    
    tournament.merge_all_picks(picksets)

    # Write Level Headers
    for level, starting_col in enumerate((1, 4, 7, 9), start=1):
        width = 2 if level > 2 else 3
        if tid is not None:
            starting_col = 2*starting_col - 1
            width *= 2

        worksheet.merge_range(0, starting_col, 0, starting_col +
                              width - 1, "Level %d" % level, bold_center_format)

    name_column_width = 18
    points_column_width = 4
    total_column = 22

    # Write total header
    if tid is not None:
        worksheet.set_column(0, total_column, points_column_width+1)
        worksheet.write(0, total_column, "Total", bold_center_format)

    # Write Pick Rows
    for row, pickset in enumerate(tournament.picksets, start=1):
        # Write Pickset
        worksheet.set_column(row, 0, name_column_width)
        worksheet.write(row, 0, pickset.name, italic_format)

        # Write Picks
        col = 1
        total = 0
        for player in pickset.picks:
            worksheet.set_column(row, col, name_column_width)
            worksheet.write(row, col, player.name)  # Write player

            if tid is not None:  # Write player points
                col += 1
                pl2 = func_find(tournament.players,
                                lambda pl: pl.id == player.id)
                worksheet.write(
                    row, col, pl2.points if pl2 is not None else None, points_cell_format)
                worksheet.set_column(row, col, points_column_width)

                if pl2 is not None:
                    total += pl2.points

            col += 1

        if tid is not None:
            worksheet.write(row, total_column, total)  # Write total points


def write_picks_workbook(tid_list, year, filename) -> None:
    workbook = xlsx.Workbook(filename)

    picksets = get_all_picks(year, separate=False)

    for tid, tournament_name in tid_list:
        write_picks_worksheet(workbook, tournament_name, tid, year, picksets)

    workbook.close()
