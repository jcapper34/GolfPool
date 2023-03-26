import os

# =======================
# Helpers
# =======================
def parse_bool(val):
    if isinstance(val, bool):
        return val

    try:
        return bool(eval(val))
    except Exception:
        return None

# =======================
# Database Credentials
# =======================
DATABASE_CONNECTION_STRING = os.getenv("DB_CONNECTION_STRING")

# =======================
# Point Map
# =======================
POINT_MAP = {
    "1": 100,
    "2": 75,
    "3": 65,
    "4": 60,
    "5": 55,
    "6": 50,
    "7": 45,
    "8": 40,
    "9": 35,
    "10": 30,
    "11": 25,
    "12": 20,
    "13": 16,
    "14": 12,
    "15": 9,
    "16": 6,
    "17": 4,
    "18": 3,
    "19": 2,
    "20": 1
}

# =======================
# Paths
# =======================
XL_DIR = 'web/static/generated/xl/'


# =======================
# Maps
# =======================
TOURNAMENT_NAME_MAP = {
    "014": "The Masters",
    "026": "U.S Open",
    "100": "British Open",
    "033": "PGA Championship",
}

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
TOUR_PHOTO_URL = "https://pga-tour-res.cloudinary.com/image/upload/c_fill,d_headshots_default.png,dpr_2.0,f_auto,g_face:center,h_300,q_auto,w_300/headshots_%s.png"
TOUR_PLAYERS_URL = "https://statdata.pgatour.com/players/player.json"

# From Golf Channel Website
ACTIVE_EVENTS_URL = "https://www.golfchannel.com/api/v2/events/active"
STAT_CATEGORIES_URL = "https://www.golfchannel.com/api/v2/tours/1/stats/categories"
OWGR_STAT_ID = 19   # For OWGR ranking
# Parameters: Stat Number, year
STATS_URL = "https://www.golfchannel.com/api/v2/tours/1/stats/%d/%d"
GOLFERS_URL = "https://www.golfchannel.com/api/es/fullObject"
# Parameters: pid
INDIVIDUAL_GOLFER_URL = "https://www.golfchannel.com/api/v2/golfers/%s/full"

# =======================
# Routing Aliases
# =======================
ROUTING_ALIASES = (
    ("/picksets/make", "picks.picks_make"),
    ("/picksets/change", "picks.picks_change"),
    ("/standings/live", "results.results_live"),
    ("/standings/<int:year>/<tid>", "results.results_past")
)

SRC_LOCAL = parse_bool(os.getenv("SRC_LOCAL", True))
PICKS_LOCKED = parse_bool(os.getenv("PICKS_LOCKED", True))
UNLOCK_ALL_PAGES = parse_bool(os.getenv("UNLOCK_ALL_PAGES", False))

# Database credentials
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_HOSTNAME = os.getenv("DB_HOSTNAME")
DB_PORT = os.getenv("DB_PORT")
DB_SSLMODE = os.getenv("DB_SSLMODE")

# If you want to override which tournament is used for live
LIVE_TOURNAMENT_OVERRIDE_ID = os.getenv("LIVE_TOURNAMENT_OVERRIDE_ID")
LIVE_TOURNAMENT_OVERRIDE_YEAR = os.getenv("LIVE_TOURNAMENT_OVERRIDE_YEAR")
