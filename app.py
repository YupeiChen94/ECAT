from flask import Flask
from flask_caching import Cache
import dash
import dash_bootstrap_components as dbc
import uuid

config = {
    'CACHE_TYPE': 'filesystem',
    'CACHE_DEFAULT_TIMEOUT': 300,
    'CACHE_DIR': '/tmp',
    'CACHE_THRESHOLD': 200
}

server = Flask(__name__)
app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.SPACELAB], suppress_callback_exceptions=True)
cache = Cache(app.server, config=config)
session_id = str(uuid.uuid4())

# TODO: Disable graph options tab until data is queried? Notification to please requery if benchmarking is toggled?
# TODO: AD Security
# TODO: Increase graph height for 3D plot
# TODO: Standard Graphs, PDF download?
# TODO: Graphic Customizations

# TODO: Legend to plot multiple variables at a time
# TODO: Benchmarking for multiple refinerys at once
# TODO: Filter by result value post query, popup with dynamic selections?
# TODO: Trendline for benchmarking

# TODO: Options for regression line to be turned off
# TODO: Labels missing on benchmarking
# TODO: Increase cache to 200
