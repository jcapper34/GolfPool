from flask import Blueprint

picks_mod = Blueprint("picks", __name__, template_folder='templates')

# Root of Picks Module
@picks_mod.route("/")
def picks_index():
    return "Hello Picks"
