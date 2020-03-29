import xlrd

from db.conn import Conn
from helper import func_find, get_json
from picksets.pickset import Pickset
from picksets.picksets_db import get_all_picks
from players.player import Player
from players.players_helper import level_separate


def xl_parse_picks(file_name, year):
    conn = Conn()
    api_players = list(get_json(Player.GOLFERS_URL)['items'].values())
    all_players = [Player(**pl) for pl in conn.exec_fetch("SELECT id as pid, name FROM player")]

    wb = xlrd.open_workbook(file_name)
    sheet = wb.sheet_by_index(0)

    print(sheet.merged_cells)

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

            pickset.picks.append(Player(name=name))

        # pickset.picks = level_separate(pickset.picks[])
        # pickset.db_inserts(year, conn=conn)





if __name__ == "__main__":
    xl_parse_picks('xlsx/picks-2017.xlsx', 2017)