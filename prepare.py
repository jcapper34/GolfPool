# This script will be run to setup everything and test before the server starts
import os
import sass

from picksets.pickset import Pickset
from players.player import Player
from tournament.tournament_calculations import calculate_standings
from tournament.tournament_retriever import get_api_tournament

WEB_DIR = 'web'


def compile_sass():
    for entry in os.scandir(WEB_DIR):
        if entry.is_dir():
            if entry.name == 'sass':
                sass_dir = os.path.join(WEB_DIR, 'sass')
                css_dir = os.path.join(WEB_DIR, 'static/css')
            else:
                sass_dir = os.path.join(WEB_DIR, entry.name, 'sass')
                css_dir = os.path.join(WEB_DIR, entry.name, 'static/css')

            if os.path.exists(sass_dir):
                if not os.path.exists(css_dir):
                    os.mkdir(css_dir)

                for sass_entry in os.scandir(sass_dir):
                    if sass_entry.is_file():
                        sass_filename = os.path.join(sass_dir, sass_entry.name)

                        css_out = sass.compile(filename=sass_filename,
                                               output_style='compressed', include_paths=["web/sass"])
                        css_filename = os.path.join(
                            css_dir, sass_entry.name.split(".")[0] + '.min.css')
                        with open(css_filename, 'w') as f:
                            f.write(css_out)
                            print("Compiled SASS into", css_filename)


def test_standings_calculations():
    print("[test_standings_calculations] Starting test")
    picksets = [
        Pickset(
            id=1,
            picks=[Player(id=1), Player(id=4), Player(id=5), Player(id=9)]
        ),
        Pickset(
            id=2,
            picks=[Player(id=1), Player(id=2), Player(id=3), Player(id=6)]
        ),
        Pickset(
            id=3,
            picks=[Player(id=2), Player(id=4), Player(id=5), Player(id=7)]
        ),
        Pickset(
            id=4,
            picks=[Player(id=1), Player(id=4), Player(id=7), Player(id=9)]
        )
    ]
    
    players = [
        Player(id=2, points=100),
        Player(id=1, points=75),
        Player(id=7, points=65),
        Player(id=3, points=60),
        Player(id=4, points=55)
    ]
    
    picksets = calculate_standings(players, picksets)
        
    assert picksets[0].id == 2
    assert picksets[0].points == 235
    
    assert picksets[1].id == 3
    assert picksets[1].points == 220

    assert picksets[2].id == 4
    assert picksets[2].points == 195
    
    assert picksets[3].id == 1
    assert picksets[3].points == 130

    print("[test_standings_calculations] Test completed successfully")


def test_api():
    print("[test_api] Starting test")
    assert get_api_tournament('459e9ffb-1eb4-422c-9f13-1ba8344c35aa') is not None
    print("[test_api] Test completed successfully")

if __name__ == "__main__":
    compile_sass()
    
    # Tests
    test_standings_calculations()
    test_api()
