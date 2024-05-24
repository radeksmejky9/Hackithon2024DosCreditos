from app import app
from flask import render_template
from app.mqtt_client import mqtt_data
from dash import dcc, html, Input, Output

layout = html.Div(
    [
        html.H1("MQTT Data"),
        dcc.Graph(id="mqtt_graph"),
        dcc.Interval(
            id="interval-component", interval=1000, n_intervals=0  # in milliseconds
        ),
    ]
)
app.layout = layout


@app.callback(
    Output("mqtt_graph", "figure"), [Input("interval-component", "n_intervals")]
)
def update_graph(n):
    # Process mqtt_data to create a graph figure
    x = [data["timestamp"] for data in mqtt_data]
    y = [data["size"] for data in mqtt_data]
    topics = [data["topic"] for data in mqtt_data]

    traces = []
    for topic in set(topics):
        x_topic = [x[i] for i in range(len(x)) if topics[i] == topic]
        y_topic = [y[i] for i in range(len(y)) if topics[i] == topic]
        traces.append(dict(x=x_topic, y=y_topic, mode="markers+lines", name=topic))

    return {
        "data": traces,
        "layout": {
            "title": "MQTT Data",
            "xaxis": {"title": "Timestamp"},
            "yaxis": {"title": "Size"},
        },
    }


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
