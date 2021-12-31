from urllib.parse import urlparse
from flask import Flask, render_template, redirect, url_for, request, jsonify
from requests import get as http_get
import logging

import picks
import results
import rest
from config import USE_LOCAL
from flask_cors import CORS

app = Flask(__name__)   # Creates app

logging.basicConfig(format='[%(asctime)s] - %(message)s', level=logging.INFO)
logging.info("Using local database" if USE_LOCAL else "Using heroku database")

# Allow Cross Origin
CORS(app)

app.secret_key = b'=\x06\x9f}\x97\xe9\x88\xba\xd0\xaa\xe7r\x82\x94\x8a\xb8m\x84\xc34%Bu\xc5'    # Key for sessions

""" REGISTER BLUEPRINTS """
app.register_blueprint(picks.routes.picks_mod, url_prefix='/picks')
app.register_blueprint(results.routes.results_mod, url_prefix='/results')
app.register_blueprint(rest.routes.api_mod, url_prefix='/api')


""" ROUTES BEGIN """
@app.route("/")
def index():
    return render_template("home.html")


""" Aliases """
@app.route("/picksets/make")
def picks_make_alias():
    return redirect(url_for('picks.picks_make'))

@app.route("/picksets/change")
def picks_change_alias():
    return redirect(url_for('picks.picks_change'))

@app.route("/standings/live")
def results_live_alias():
    return redirect(url_for('results.results_live'))

@app.route("/standings/<int:year>/<tid>")
def results_past_alias(year, tid):
    return redirect(url_for('results.results_past', year=year, tid=tid))


@app.route('/test')
def test_page():
    return render_template('test.html')


""" HELPERS """
@app.route("/api-retriever", methods=['POST'])
def api_retriever():
    url = request.form.get("url")
    if urlparse(url).netloc == 'www.golfchannel.com':   # Ensures that request goes to api
        return jsonify(http_get(url).json())

    return jsonify({})

""" Error Pages """
@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404

@app.errorhandler(500)
def page_not_found(e):
    # note that we set the 500 status explicitly
    return render_template('500.html'), 500

""" JINJA GLOBALS """
@app.context_processor
def is_local():
    return dict(is_local=USE_LOCAL)

def are_levels_defined(players):
    return any([pl.level != 4 for pl in players])
app.jinja_env.globals['are_levels_defined'] = are_levels_defined

if __name__ == "__main__":
    app.run()   # Run