from collections import Counter, deque
from app import app, redisClient
from flask import render_template
from app.mqtt_client import TOPICS, message_count
from dash import dcc, html, Input, Output
import datetime

start_time = datetime.datetime.now()
messages_per_minute_history = deque(maxlen=50)

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
        dcc.Graph(id="top_transfers_graph_pie"),
        dcc.Graph(id="req_per_min_graph"),
        dcc.Interval(
            id="interval-component", interval=1000, n_intervals=0  # in milliseconds
        ),
    ]
)
app.layout = layout

data = []


# Callback for updating MQTT data graph
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

    data = get_data(traces=traces, layout=layout)

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


@app.callback(
    Output("top_size_graph", "figure"),
    [Input("interval-component", "n_intervals")],
)
def update_top_size_graph(n):
    layout = {
        "title": "Top Size Transferred Over Time",
        "xaxis": {"title": "Topic"},
        "yaxis": {"title": "Total Size Transferred"},
    }
    data = get_data(layout=layout)
    top_size_topics = sorted(
        data.keys(),
        key=lambda x: sum(d["size"] for d in data[x]),
        reverse=True,
    )[:5]
    top_size_values = [
        sum(data["size"] for data in data[topic]) for topic in top_size_topics
    ]

    top_size_figure = {
        "data": [{"x": top_size_topics, "y": top_size_values, "type": "bar"}],
        "layout": layout,
    }

    return top_size_figure


@app.callback(
    Output("top_transfers_graph", "figure"),
    [Input("interval-component", "n_intervals")],
)
def update_top_transfers_graph(n):
    layout = {"title": "Top Transfers"}
    data = get_data(layout=layout)

    transfer_counts = Counter(
        [data["topic_readable"] for topic in data.values() for data in topic]
    )
    top_transfers = dict(
        sorted(transfer_counts.items(), key=lambda item: item[1], reverse=True)[:5]
    )
    top_transfers_figure = {
        "data": [
            {
                "x": list(top_transfers.keys()),
                "y": list(top_transfers.values()),
                "type": "bar"
            }
        ],
        "layout": layout,
    }
    return top_transfers_figure


@app.callback(
    Output("top_transfers_graph_pie", "figure"),
    [Input("interval-component", "n_intervals")],
)
def update_top_transfers_graph(n):
    layout = {"title": "Top Transfers"}
    data = get_data(layout=layout)

    transfer_counts = Counter(
        [data["topic_readable"] for topic in data.values() for data in topic]
    )
    top_transfers = dict(
        sorted(transfer_counts.items(), key=lambda item: item[1], reverse=True)[:5]
    )
    top_transfers_graph_pie = {
        "data": [
            {
                "labels": list(top_transfers.keys()),
                "values": list(top_transfers.values()),
                "type": "pie",
                "domain": {"x": [0.1, 1], "y": [0, 1]}
            }
        ],
        "layout": layout,
    }
    return top_transfers_graph_pie


@app.callback(
    Output("req_per_min_graph", "figure"),
    [Input("interval-component", "n_intervals")],
)
def update_req_per_min_graph(n):
    global messages_per_minute_history

    layout = {
        "title": "Messages per Minute",
        "xaxis": {"title": "Time"},
        "yaxis": {"title": "Messages per Minute"},
    }
    data = get_data(layout=layout)
    current_time = datetime.datetime.now()
    elapsed_time = (current_time - start_time).total_seconds()

    if elapsed_time > 0:
        messages_per_minute = len(data) / (elapsed_time / 60)

    messages_per_minute_history.append([current_time, messages_per_minute])

    req_per_min_figure = {
        "data": [
            {
                "x": [record[0] for record in messages_per_minute_history],
                "y": [record[1] for record in messages_per_minute_history],
                "type": "scatter",
                "mode": "lines",
                "name": "Messages per Minute",
            }
        ],
        "layout": layout,
    }

    return req_per_min_figure


# @app.callback(
#     Output("top_transfers_graph", "figure"),
#     [Input("interval-component", "n_intervals")],
# )
# def total_stability(n):
#     layout = {"title": "Top Transfers"}
#     data = get_data()

#     transfer_counts = Counter(
#         [data["topic_readable"] for topic in data.values() for data in topic]
#     )
#     top_transfers = dict(
#         sorted(transfer_counts.items(), key=lambda item: item[1], reverse=True)[:5]
#     )
#     top_transfers_figure = {
#         "data": [
#             {
#                 "x": list(top_transfers.keys()),
#                 "y": list(top_transfers.values()),
#                 "type": "bar",
#             }
#         ],
#         "layout": layout,
#     }
#     return top_transfers_figure


@app.server.route("/")
def index():
    return "lorem"


@app.server.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.server.route("/hello")
def hello():
    return "Hello, World!"


def get_data(traces=[], layout={}):
    data = redisClient.get_messages()

    if data == []:
        return {"data": traces, "layout": layout}

    return data
