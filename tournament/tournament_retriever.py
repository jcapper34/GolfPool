import json
from typing import Dict
from datetime import datetime

from config import LEADERBOARD_URL, POINT_MAP
from globalcache import GlobalCache
from helper import request_json
from players.player import Player
from tournament.tournament import Tournament


def get_api_tournament(channel_tid=None) -> Tournament:
    channel_tid = channel_tid if channel_tid is not None else GlobalCache.current_tid
    api_data = request_json(LEADERBOARD_URL % channel_tid)
    api_tournament = api_data.get('result')

    leaderboard = api_tournament['golfers']
    
    tournament = Tournament()
    tournament.channel_tid = channel_tid
    tournament.year = datetime.strptime(api_data['latestOddsUpdate'], "%B %d, %Y").year
    tournament.channel_tid = api_tournament.get('eventKey')
    tournament.scorecards = api_tournament['scorecards']

    tournament.players = [Player(id=pl['golferId'],
                           name=pl['firstName'] + " " + pl['lastName'],
                           pos=pl['position'] if pl['sortHelp'] is not None and pl['sortHelp'] < 1000 else None,
                           points=POINT_MAP[str(pl['sortHelp'])] if pl['sortHelp'] is not None and pl['sortHelp'] <= 20 else 0,
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
