from flask import Flask
from dash import Dash

server = Flask(__name__)
app = Dash(__name__, server=server)

from app import routes
