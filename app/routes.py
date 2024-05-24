from app import app
from flask import render_template, jsonify
from app.mqtt_client import mqtt_data


@app.route("/")
def index():
    return "lorem"


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/get_data")
def get_data():
    return jsonify({"mqtt_data": mqtt_data})
