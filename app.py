from flask import Flask, render_template, render_template_string
import picks, results

# Creates app
app = Flask(__name__)

# Key for sessions
app.secret_key = b'=\x06\x9f}\x97\xe9\x88\xba\xd0\xaa\xe7r\x82\x94\x8a\xb8m\x84\xc34%Bu\xc5'

# Registering blueprints
app.register_blueprint(picks.routes.picks_mod, url_prefix='/picks')
app.register_blueprint(results.routes.results_mod, url_prefix='/results')


### ROUTES BEGIN ###

@app.route("/")
def index():
    return render_template("home.html")


if __name__ == "__main__":
    app.run()