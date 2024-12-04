from urllib.parse import urlparse
from http import HTTPStatus
from flask import Flask, render_template, redirect, url_for, request, jsonify
from requests import get as http_get
import logging
from cronjobs import start_jobs
from helpers import CURRENT_YEAR, request_json
from web.jinjafilters import register_filters

from web.picks.picks_routes import mod as picks_mod
from web.results.results_routes import mod as results_mod
from web.api.api_routes import mod as api_mod
from config import ROUTING_ALIASES, SRC_LOCAL
from flask_cors import CORS

app = Flask(__name__, static_folder='web/static', template_folder='web/templates')   # Creates app

# Allow Cross Origin
CORS(app)

# Key for sessions
app.secret_key = b'=\x06\x9f}\x97\xe9\x88\xba\xd0\xaa\xe7r\x82\x94\x8a\xb8m\x84\xc34%Bu\xc5'

# ========================
#       Logging
# ========================
logging.basicConfig(format='[%(asctime)s] - %(message)s', level=logging.INFO)

# ========================
# Register Blueprints
# ========================
app.register_blueprint(picks_mod, url_prefix='/picks')
app.register_blueprint(results_mod, url_prefix='/results')
app.register_blueprint(api_mod, url_prefix='/api')

# ========================
# Register Jinja Filters
# ========================
register_filters(app)

# ========================
# Start Cron Jobs
# ========================
start_jobs()

# =======================
#   Routes Begin
# =======================
@app.route("/")
def index():
    return render_template("home.html", year=CURRENT_YEAR)


# =======================
#       Aliases
# =======================
def alias_handlers(dest):
    def reroute(**kwargs): 
        return redirect(url_for(dest, **kwargs))
    
    return reroute
    
for i, pair in enumerate(ROUTING_ALIASES):
    app.add_url_rule(pair[0], "alias"+str(i), alias_handlers(pair[1]))


@app.route('/test')
def test_page():
    return render_template('test.html')


# ========================
# Helpers
# ========================
@app.route("/api-retriever", methods=['POST'])
def api_retriever():
    proxy_whitelist = {"www.golfchannel.com", "apiweb.owgr.com", "production.api.golf.com"}

    url = request.form.get("url")
    if urlparse(url).netloc in proxy_whitelist:   # Ensures that request goes to api
        return jsonify(request_json(url))

    return jsonify({})

# ========================
# Error Pages
# ========================
@app.errorhandler(HTTPStatus.NOT_FOUND)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), HTTPStatus.NOT_FOUND

@app.errorhandler(HTTPStatus.INTERNAL_SERVER_ERROR)
def page_not_found(e):
    # note that we set the 500 status explicitly
    return render_template('500.html'), HTTPStatus.INTERNAL_SERVER_ERROR

# ========================
# Jinja Globals
# ========================
@app.context_processor
def retrieve_src_local():
    return dict(src_local=SRC_LOCAL)

if __name__ == "__main__":
    app.run()   # Run
