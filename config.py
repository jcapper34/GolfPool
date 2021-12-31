from os import environ

from helper import RUNNING_LOCALLY

USE_LOCAL = RUNNING_LOCALLY    # Will be true if running locally
# USE_LOCAL = False   # Uncomment if you want to use the remote DB locally

LOCAL_DB_CREDENTIALS = {
            "dbname": 'postgres',
            "user": 'jcapp',
            "host": 'localhost',
            "password": 'cmcapper',
            "options": '-c search_path=golfpool'
}

HEROKU_DB_CREDENTIALS = {
            "dbname": 'd494jt3e43ugjm',
            "user": 'dnydvecerfhlus',
            "host": 'ec2-3-215-52-251.compute-1.amazonaws.com',
            "password": '5bb791bfdcb7afa07b23f9703f9e3091c3d52459f4bfd0390afcc6938e9a0af5',
            "options": '-c search_path=golfpool'
}

# Golf Channel URL
# Parameters: int[tid]
LEADERBOARD_URL = "https://www.golfchannel.com/api/v2/events/%d/leaderboard"
# Parameters: int[year]
EVENTS_URL = "https://www.golfchannel.com/api/v2/tours/1/events/%d"
# Parameters: int[tid]
ALL_SCORECARDS_URL = "https://www.golfchannel.com/api/v2/events/%d/scorecard"


# From PGA Tour Website
PGA_PHOTO_URL = "https://pga-tour-res.cloudinary.com/image/upload/c_fill,d_headshots_default.png,dpr_2.0,f_auto,g_face:center,h_300,q_auto,w_300/headshots_%s.png"
# OWGR_URL = "https://statdata.pgatour.com/r/stats/%s/186.json"   # Takes year as argument
ALL_PLAYERS_URL = "https://statdata.pgatour.com/players/player.json"

# From Golf Channel Website
STAT_CATEGORIES_URL = "https://www.golfchannel.com/api/v2/tours/1/stats/categories"
OWGR_STAT_ID = 19   # For OWGR ranking
STATS_URL = "https://www.golfchannel.com/api/v2/tours/1/stats/%d/2021"   # Parameters: Stat Number
GOLFERS_URL = "https://www.golfchannel.com/api/es/fullObject"