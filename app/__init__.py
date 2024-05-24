from flask import Flask
from app import mqtt_client

app = Flask(__name__)


from app import routes
