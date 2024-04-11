import os

# =======================
# Helpers
# =======================
def get_bool(key: str, default: bool):
    val = os.getenv(key, default)
    
    if isinstance(val, bool):
        return val

    try:
        return bool(eval(val.capitalize()))
    except Exception:
        return default


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
# Golf.com API
# =======================
LEADERBOARD_URL = "https://production.api.golf.com/api/v1/tournaments/full-leaderboard/%s" # Parameters: string[tid]
EVENTS_URL = "https://production.api.golf.com/api/v1/tournament-schedule/%d/pga" # Parameters: int[year]
GOLF_RANKINGS_URL = "https://production.api.golf.com/api/v1/rankings/official-world-ranking"

# =======================
# Golf Channel API
# =======================
STATS_URL = "https://www.golfchannel.com/api/v2/tours/1/stats/%d/%d" # Parameters: Stat Number, year
INDIVIDUAL_GOLFER_URL = "https://www.golfchannel.com/api/v2/golfers/%s/full" # Parameters: pid

# =======================
# PGA Tour API
# =======================
TOUR_PHOTO_URL = "https://pga-tour-res.cloudinary.com/image/upload/c_fill,d_headshots_default.png,dpr_2.0,f_auto,g_face:center,h_300,q_auto,w_300/headshots_%s.png" # Parameters: int[pid]
TOUR_PLAYERS_URL = "https://statdata.pgatour.com/players/player.json"

# =======================
# OWGR API
# =======================
OWGR_DATA_HASH = os.getenv("OWGR_DATA_HASH", "GtoJ9xPTdmOVfHsMXSiAe")
OWGR_PAGE_SIZE_MAKE_PICKS = 250
OWGR_RANKINGS_URL = "https://apiweb.owgr.com/api/owgr/rankings/getRankings?regionId=0&pageSize=%d&pageNumber=%d&countryId=0&sortString=Rank+ASC" # Parameters: int[pageSize], int[pageNumber]
OWGR_LEADERBOARD_URL = "https://www.owgr.com/_next/data/" + OWGR_DATA_HASH + "/events/%d.json" # Parameters: int[tid]

# Headers will emulate browser
BROWSER_EMULATE_HEADERS = {
    # "Host": "production.api.golf.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Sec-GPC": "1",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache"
}

# =======================
# Routing Aliases
# =======================
ROUTING_ALIASES = (
    ("/picksets/make", "picks.picks_make"),
    ("/picksets/change", "picks.picks_change"),
    ("/standings/live", "results.results_live"),
    ("/standings/<int:year>/<tid>", "results.results_past")
)

SRC_LOCAL = get_bool("SRC_LOCAL", True)
PICKS_LOCKED = get_bool("PICKS_LOCKED", True)
UNLOCK_ALL_PAGES = get_bool("UNLOCK_ALL_PAGES", False)

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
LIVE_TOURNAMENT_OVERRIDE_NAME = os.getenv("LIVE_TOURNAMENT_OVERRIDE_NAME")

# Feature controls
ENABLE_THREADED_DB_CONN = get_bool("ENABLE_THREADED_DB_CONN", True)