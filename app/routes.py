from app import app
from app import templates
from flask import render_template


@app.route("/")
def index():
    return "cs"


@app.route("/items")
def items():
    items = [
        {"name": "Item 1", "completed": False},
        {"name": "Item 2", "completed": True},
        {"name": "Item 3", "completed": False},
    ]
    return render_template("items.html", items=items)
