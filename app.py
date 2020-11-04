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

# TODO: Download button for current cached data
# TODO: AD Security
# TODO: Remove create/update date from axis selector
# TODO: Remove M000 PSD from axis selector
# TODO: Benchmarking: All refinerys, user sample type and date, but highlighting a specific refinery
