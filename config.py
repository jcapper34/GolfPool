import os

# =======================
# Database Credentials
# =======================

LOCAL_DB_CREDENTIALS = os.getenv('LOCAL_DATABASE_URL')

HEROKU_DB_CREDENTIALS = os.getenv('DATABASE_URL')

# =======================
# Golf Channel API
# =======================

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

# =======================
# Routing Aliases
# =======================
ROUTING_ALIASES = (
    ("/picksets/make", "picks.picks_make"),
    ("/picksets/change", "picks.picks_change"),
    ("/standings/live", "results.results_live"),
    ("/standings/<int:year>/<tid>", "results.results_past")
)

USE_LOCAL = os.getenv("USE_LOCAL").lower() == 'true'