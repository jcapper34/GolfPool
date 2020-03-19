from helper import CURRENT_YEAR
from db.conn import Conn


def insert_levels(year=CURRENT_YEAR):
    levels = (
        (
         'Rory McIlroy',
         'Jon Rahm',
         'Brooks Koepka',
         'Justin Thomas',
         'Dustin Johnson',
         'Adam Scott',
         'Patrick Reed',
         'Patrick Cantlay',
         'Webb Simpson',
         'Tommy Fleetwood',
         'Tiger Woods',
         'Justin Rose'
        ),
        (
        'Xander Schauffele',
        'Bryson DeChambeau',
        'Marc Leishman',
        'Tony Finau',
        'Matt Kuchar',
        'Gary Woodland',
        'Louis Oosthuizen',
        'Shane Lowry',
        'Tyrrell Hatton',
        'Hideki Matsuyama',
        'Paul Casey',
        'Matthew Fitzpatrick',
        'Rickie Fowler',
        'Henrik Stenson',
        'Sergio Garcia',
        'Jordan Spieth',
        'Jason Day',
        'Bubba Watson'
        ),
        (
        'Sungjae Im',
        'Bernd Wiesberger',
        'Francesco Molinari',
        'Abraham Ancer',
        'Kevin Na',
        'Lee Westwood',
        'Danny Willett',
        'Billy Horschel',
        'Cameron Smith',
        'Kevin Kisner',
        'Chez Reavie',
        'Rafa Cabrera Bello',
        'Jazz Janewattananond',
        'Scottie Scheffler',
        'Brandt Snedeker',
        'Graeme McDowell',
        'Ian Poulter',
        'Phil Mickelson',
        'Keegan Bradley',
        'Branden Grace',
        'Adam Hadwin',
        )
    )
    conn = Conn()

    # Do clean up
    conn.exec_commit("DELETE FROM level_xref WHERE season_year = %s", (year,))

    for level_num in range(1, len(levels)+1):
        for player_name in levels[level_num-1]:
            results = conn.exec_fetch("SELECT id FROM player WHERE name=%s", (player_name,), fetchall=False)    # Get player id
            if results is None:
                print("Player %s does not exist" % player_name)
                continue
            pid = results[0]
            conn.exec("INSERT INTO level_xref (player_id, season_year, level) VALUES(%s,%s,%s)", (pid, year, level_num))

    conn.commit()




if __name__ == "__main__":
    insert_levels(2020)