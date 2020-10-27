from flask import Flask
from flask_caching import Cache
import dash
import dash_bootstrap_components as dbc
import uuid

config = {
    'CACHE_TYPE': 'filesystem',
    'CACHE_DEFAULT_TIMEOUT': 300,
    'CACHE_DIR': '/tmp',
    'CACHE_THRESHOLD': 10
}

server = Flask(__name__)
app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.SPACELAB], suppress_callback_exceptions=True)
cache = Cache(app.server, config=config)
session_id = str(uuid.uuid4())
