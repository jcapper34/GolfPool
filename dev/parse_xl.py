import xlrd
from config import GOLFERS_URL

from db.conn import Conn
from helper import func_find, request_json, splash
from picksets.pickset import Pickset
from picksets.picksets_db import get_all_picks
from players.player import Player
from players.players_helper import level_separate


def xl_parse_picks(file_name, year, delete_first=False):
    conn = Conn()
    if delete_first:
        conn.exec("DELETE FROM pickset WHERE season_year=%s", (year,))

    api_players = list(request_json(GOLFERS_URL)['items'].values())
    all_players = [Player(**pl) for pl in conn.exec_fetch("SELECT id, name FROM player")]

    wb = xlrd.open_workbook(file_name)
    sheet = wb.sheet_by_index(0)

    rows_gen = sheet.get_rows()
    next(rows_gen)  # Skip first row

    for row in rows_gen:
        row = list(filter(lambda r: r.ctype != 0 and r.value.strip(), row)) # Remove empty cells

        pickset = Pickset(name=row.pop(0).value, picks=[])

        if len(row) != 10:
            print("Unequal number of picks", pickset.name)
            break

        for col, player in enumerate(row, start=1):
            name = player.value.strip()
            match = func_find(all_players, lambda pl: pl.name.lower() == name.lower())
            if match is None:
                match = func_find(api_players, lambda pl: pl['name'].lower() == name.lower())
                if match is None:
                    print("Doesn't exist", name)
                    continue

            pickset.picks.append(Player(name=name, id=match.id))

        pickset.db_inserts(year, conn=conn)

if __name__ == "__main__":
    xl_parse_picks('xlsx/picks-2016.xlsx', 2016, delete_first=True)