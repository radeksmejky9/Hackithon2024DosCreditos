from app import app
from flask import render_template, jsonify
from app.mqtt_client import mqtt_data, TOPICS
from dash import dcc, html, Input, Output
import datetime
from collections import Counter

# Define layout with multiple graphs
layout = html.Div(
    [
        html.H1("MQTT Data flow"),
        dcc.Graph(
            id="mqtt_graph",
            figure={
                "data": [
                    {
                        "x": [],
                        "y": [],
                        "mode": "markers+lines",
                        "name": "Placeholder",
                    }
                ],
                "layout": {
                    "title": "MQTT Data",
                    "xaxis": {"title": "Timestamp"},
                    "yaxis": {"title": "Size"},
                },
            },
        ),
        dcc.Graph(id="top_size_graph"),
        dcc.Graph(id="top_transfers_graph"),
        dcc.Interval(
            id="interval-component", interval=1000, n_intervals=0  # in milliseconds
        ),
    ]
)
app.layout = layout


# Callback for updating MQTT data graph
@app.callback(
    Output("mqtt_graph", "figure"),
    [Input("interval-component", "n_intervals")],
)
def update_graph(n):
    traces = []

    for topic_key in TOPICS.keys():
        traces.append(
            {
                "x": [],
                "y": [],
                "mode": "markers+lines",
                "name": TOPICS[topic_key],
            }
        )
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

    return {"data": traces, "layout": layout}


# Callback for updating graph displaying topics with highest size transferred over time
@app.callback(
    Output("top_size_graph", "figure"), [Input("interval-component", "n_intervals")]
)
def update_top_size_graph(n):
    top_size_topics = sorted(
        mqtt_data.keys(),
        key=lambda x: sum(d["size"] for d in mqtt_data[x]),
        reverse=True,
    )[:5]
    top_size_values = [
        sum(data["size"] for data in mqtt_data[topic]) for topic in top_size_topics
    ]

    top_size_figure = {
        "data": [{"x": top_size_topics, "y": top_size_values, "type": "bar"}],
        "layout": {
            "title": "Top Size Transferred Over Time",
            "xaxis": {"title": "Topic"},
            "yaxis": {"title": "Total Size Transferred"},
        },
    }

    return top_size_figure


# Callback for updating graph displaying highest amount of transfers made so far
@app.callback(
    Output("top_transfers_graph", "figure"),
    [Input("interval-component", "n_intervals")],
)
def update_top_transfers_graph(n):
    transfer_counts = Counter(
        [data["topic_readable"] for topic in mqtt_data.values() for data in topic]
    )
    top_transfers = dict(
        sorted(transfer_counts.items(), key=lambda item: item[1], reverse=True)[:5]
    )
    top_transfers_figure = {
        "data": [
            {
                "x": list(top_transfers.keys()),
                "y": list(top_transfers.values()),
                "type": "bar",
            }
        ],
        "layout": {"title": "Top Transfers"},
    }
    return top_transfers_figure


@app.callback(
    Output("top_transfers_graph", "figure"),
    [Input("interval-component", "n_intervals")],
)
def total_stability(n):
    transfer_counts = Counter(
        [data["topic_readable"] for topic in mqtt_data.values() for data in topic]
    )
    top_transfers = dict(
        sorted(transfer_counts.items(), key=lambda item: item[1], reverse=True)[:5]
    )
    top_transfers_figure = {
        "data": [
            {
                "x": list(top_transfers.keys()),
                "y": list(top_transfers.values()),
                "type": "bar",
            }
        ],
        "layout": {"title": "Top Transfers"},
    }
    return top_transfers_figure


# Define Flask routes
@app.server.route("/")
def index():
    return "lorem"


@app.server.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.server.route("/get_data")
def get_data():
    return jsonify(mqtt_data)


@app.server.route("/hello")
def hello():
    return "Hello, World!"
