from app import app
from flask import render_template
from app.mqtt_client import mqtt_data
from app.mqtt_client import TOPICS
from dash import dcc, html, Input, Output, State

layout = html.Div(
    [
        html.H1("MQTT Data flow"),
        dcc.Graph(id="mqtt_graph"),
        dcc.Interval(
            id="interval-component", interval=1000, n_intervals=0  # in milliseconds
        ),
    ]
)
app.layout = layout


@app.callback(
    Output("mqtt_graph", "figure"),
    [Input("interval-component", "n_intervals")],
    [State("mqtt_graph", "relayoutData")],
)
def update_graph(n, relayoutData):
    traces = []
    for topic_key in TOPICS.keys():
        traces.append(dict(x=[], y=[], mode="markers+lines", name=topic_key))

    # Update traces with available data
    for topic, data_list in mqtt_data.items():
        topic_index = list(TOPICS.keys()).index(topic)
        for data in data_list:
            traces[topic_index]["x"].append(data["timestamp"])
            traces[topic_index]["y"].append(data["size"])

    layout = {
        "title": "MQTT Data",
        "xaxis": {"title": "Timestamp"},
        "yaxis": {"title": "Size"},
    }

    if relayoutData:
        if "xaxis.range" in relayoutData:
            layout["xaxis"]["range"] = relayoutData["xaxis.range"]
        if "yaxis.range" in relayoutData:
            layout["yaxis"]["range"] = relayoutData["yaxis.range"]

    return {"data": traces, "layout": layout}


@app.server.route("/")
def index():
    return "lorem"


@app.server.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.server.route("/get_data")
def get_data():
    return app.index()


@app.server.route("/hello")
def hello():
    return "Hello, World!"
