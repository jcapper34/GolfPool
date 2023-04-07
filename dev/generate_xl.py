import os, sys

base_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(base_dir + "/..") # Hack to import from root

from helper.helpers import *
from db.connection_pool import db_pool
import xlsxwriter as xlsx
from pprint import pprint

from picksets.pickset_getters import get_all_picks
from tournament.tournament import Tournament
from tournament.tournament_retriever import get_db_rankings, get_db_standings


def write_picks_worksheet(workbook, w_name, tid, picksets):
    bold_center_format = workbook.add_format({'align': 'center', "bold": True})
    italic_format = workbook.add_format({'italic': True})
    points_cell_format = workbook.add_format({'align':'left'})

    worksheet = workbook.add_worksheet(w_name)

    tournament = None
    if tid is not None:
        tournament = Tournament(year=year, tid=tid)
        tournament.players = get_db_rankings(tid, year)
        tournament.picksets = get_db_standings(tid, year)
        tournament.merge_all_picks(picksets)
        picksets = tournament.picksets

    # Write Level Headers
    for level, starting_col in enumerate((1, 4, 7, 9), start=1):
        width = 2 if level > 2 else 3
        if tid is not None:
            starting_col = 2*starting_col - 1
            width *= 2

        worksheet.merge_range(0, starting_col, 0, starting_col + width - 1, "Level %d" % level, bold_center_format)

    name_column_width = 18
    points_column_width = 4
    total_column = 22

    # Write total header
    if tid is not None:
        worksheet.set_column(0, total_column, points_column_width+1)
        worksheet.write(0, total_column, "Total", bold_center_format)

    # Write Pick Rows
    for row, pickset in enumerate(picksets, start=1):
        # Write Pickset
        worksheet.set_column(row, 0, name_column_width)
        worksheet.write(row, 0, pickset.name, italic_format)

        # Write Picks
        col = 1
        total = 0
        for player in pickset.picks:
            worksheet.set_column(row, col, name_column_width)
            worksheet.write(row, col, player.name)  # Write player

            if tid is not None: # Write player points
                col += 1
                pl2 = func_find(tournament.players, lambda pl: pl.id == player.id)
                worksheet.write(row, col, pl2.points if pl2 is not None else None, points_cell_format)
                worksheet.set_column(row, col, points_column_width)

                if pl2 is not None:
                    total += pl2.points

            col += 1

        if tid is not None:
            worksheet.write(row, total_column, total) # Write total points


def write_picks_workbook(year, filename):
    workbook = xlsx.Workbook(filename)

    worksheet_names = {
        "Picks": None,
        # "Masters": "014",
        # "PGA Championship": "033",
        # "US Open": "026",
        # "British Open": "100"
    }
    picksets = get_all_picks(year, separate=False)

    for w_name, tid in worksheet_names.items():
        write_picks_worksheet(workbook, w_name, tid, picksets)

    workbook.close()


if __name__ == "__main__":
    year = 2023
    filename = os.path.join('xlsx', 'picks-%d.xlsx' % year)

    write_picks_workbook(year, filename)
