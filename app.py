from flask import Flask, render_template, render_template_string

app = Flask(__name__)
app.secret_key = b'=\x06\x9f}\x97\xe9\x88\xba\xd0\xaa\xe7r\x82\x94\x8a\xb8m\x84\xc34%Bu\xc5'

@app.route("/")
def index():
    return "HELLO WORLD"


if __name__ == "__main__":
    app.run()