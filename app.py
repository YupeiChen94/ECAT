from flask import Flask
import dash
import dash_bootstrap_components as dbc

server = Flask(__name__)
app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.SPACELAB], suppress_callback_exceptions=True)
# For multiple apps at the same address
# app = dash.Dash(__name__, server=server, url_base_pathname='/home/')
