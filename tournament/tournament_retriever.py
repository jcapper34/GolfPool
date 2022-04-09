import json
from typing import Dict
from datetime import datetime
import requests

from config import LEADERBOARD_URL, EVENTS_URL, PGA_PHOTO_URL
from helper import request_json
from players.player import Player
from tournament.tournament import Tournament


def api_get_live() -> Dict:
    # events = get_json(EVENTS_URL % CURRENT_YEAR)
    # current_tournament = func_find(events, lambda e: NOW < datetime.strptime(e['endDate'], "%Y-%m-%dT%H:%M:%S"))    # Finds first event with end date after now
    # r = requests.get(ACTIVE_EVENTS_URL)
    # current_tournament = json.loads(eval(r.content))[0]
    # print(int(current_tournament['key']))
    # return request_json(LEADERBOARD_URL % int(current_tournament['key']))
    return request_json(LEADERBOARD_URL % 19540)


def get_api_tournament(channel_tid=None) -> Tournament:
    tournament = Tournament(channel_tid=channel_tid)
    if tournament.channel_tid is None:  # If live is requested
            api_data = api_get_live()
            api_tournament = api_data['result']  # Get Tournament From API
    else:
        api_data = request_json(LEADERBOARD_URL % int(tournament.channel_tid))
        api_tournament = api_data['result']  # Get Tournament From API

    try:
        point_template = request_json('tournament/data/point-template.json')  # Load Point Template Data
    except FileNotFoundError:
        point_template = request_json('../tournament/data/point-template.json')  # Load Point Template Data

    leaderboard = api_tournament['golfers']
    
    tournament.year = datetime.strptime(api_data['latestOddsUpdate'], "%B %d, %Y").year
    tournament.channel_tid = api_tournament.get('eventKey')
    tournament.scorecards = api_tournament['scorecards']

    tournament.players = [Player(id=pl['golferId'],
                           name=pl['firstName'] + " " + pl['lastName'],
                           pos=pl['position'] if pl['sortHelp'] is not None and pl['sortHelp'] < 1000 else None,
                           points=point_template[str(pl['sortHelp'])] if pl['sortHelp'] is not None and pl['sortHelp'] <= 20 else 0,
                           raw_pos=pl['sortHelp'],
                           total=pl['overallPar'],
                           thru=pl['thruHole'],
                           photo_url=pl['imageUrl'],
                           country_flag=pl['representsCountryUrl'],
                           status=pl['status']
                           ) for i, pl in enumerate(leaderboard)]  # Create Player objects of leaderboard

    tournament.players.sort(key=lambda x: (x.raw_pos is None, x.raw_pos))     # Sort so that None is at the end
    tournament.name = api_tournament.get("eventName")
    
    return tournament
