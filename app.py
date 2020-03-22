from flask import Flask, render_template, redirect, url_for
import picks, results
from db.db_config import USE_LOCAL

app = Flask(__name__)   # Creates app

app.secret_key = b'=\x06\x9f}\x97\xe9\x88\xba\xd0\xaa\xe7r\x82\x94\x8a\xb8m\x84\xc34%Bu\xc5'    # Key for sessions

""" REGISTER BLUEPRINTS """
app.register_blueprint(picks.routes.picks_mod, url_prefix='/picks')
app.register_blueprint(results.routes.results_mod, url_prefix='/results')


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

@app.route("/tournament/live")
def results_live_alias():
    return redirect(url_for('results.results_live'))

# TODO: Past Results alias

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


if __name__ == "__main__":
    app.run()