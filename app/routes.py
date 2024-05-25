from app import app, redisClient
from flask import render_template, make_response
from app.mqtt_client import TOPICS
from dash import dcc, html, Input, Output
import json

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

data = []


@app.callback(
    Output("mqtt_graph", "figure"),
    [Input("interval-component", "n_intervals")],
)
def update_graph(n):

    traces = []
    layout = {
        "title": "MQTT Data",
        "xaxis": {"title": "Timestamp"},
        "yaxis": {"title": "Size"},
    }

    data = redisClient.get_messages()

    if data == []:
        return {"data": traces, "layout": layout}

    for topic_key in TOPICS.keys():
        traces.append(dict(x=[], y=[], mode="markers+lines", name=topic_key))

    # Update traces with available data
    for topic, data_list in data.items():
        topic_index = list(TOPICS.keys()).index(topic)
        for data in data_list:
            traces[topic_index]["x"].append(data["timestamp"])
            traces[topic_index]["y"].append(data["size"])

    # if zoom_info:
    #     for axis_name in ["axis", "axis2"]:
    #         if f"x{axis_name}.range[0]" in zoom_info:
    #             layout[f"x{axis_name}"]["range"] = [
    #                 zoom_info[f"x{axis_name}.range[0]"],
    #                 zoom_info[f"x{axis_name}.range[1]"],
    #             ]
    #         if f"y{axis_name}.range[0]" in zoom_info:
    #             layout[f"y{axis_name}"]["range"] = [
    #                 zoom_info[f"y{axis_name}.range[0]"],
    #                 zoom_info[f"y{axis_name}.range[1]"],
    #             ]

    #     if filter_info:
    #         filtered_traces = []
    #         for trace in traces:
    #             filtered_trace = dict()
    #             filtered_trace["name"] = trace["name"]
    #             filtered_trace["mode"] = trace["mode"]
    #             filtered_trace["x"] = []
    #             filtered_trace["y"] = []

    #             for x, y in zip(trace["x"], trace["y"]):
    #                 filtered_trace["x"].append(x)
    #                 filtered_trace["y"].append(y)

    #             filtered_traces.append(filtered_trace)

    #         traces = filtered_traces

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
