from app import app
from flask import render_template


@app.route("/")
def index():
    return "lorem"


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")
