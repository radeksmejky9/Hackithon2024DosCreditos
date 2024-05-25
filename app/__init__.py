from flask import Flask
from dash import Dash
from app.redisClient import RedisClient

server = Flask(__name__)
app = Dash(__name__, server=server)
redisClient = RedisClient()

from app import routes
