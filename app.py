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

# TODO: Make multiple queries and save them, option for multi-graph where parameters for each graph can be set
# TODO: Filter by result value post query, popup with dynamic selections?
# TODO: Larger x and y variables
# TODO: Remove background on plot
