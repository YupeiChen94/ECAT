from flask import Flask
import dash
import dash_table
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import pandas as pd
from datetime import date

server = Flask(__name__)
app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.SPACELAB], suppress_callback_exceptions=True)

# region Constants
directory = 'C:/Users/flute/PycharmProjects/ALB/ECAT/Resources/Input/'
# endregion

# region Initialization
tempdb = pd.read_csv(directory + 'ECAT.csv', engine='python')
reflist = tempdb[['Refinery_ID', 'Refinery_Name']].drop_duplicates()
reflist['Refinery'] = reflist['Refinery_Name'] + ' (' + reflist['Refinery_ID'].astype(str) + ')'
reflist.sort_values(by=['Refinery_ID'], inplace=True)
# print(reflist.Refinery)
samptypelist = tempdb['Sample_Type'].drop_duplicates()
# print(samptypelist.head())
# endregion

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Information", href="/page/Information")),
        dbc.NavItem(dbc.NavLink("Query", href="/page/Query")),
        dbc.NavItem(dbc.NavLink("Options", href="/page/Options")),
        dbc.NavItem(dbc.NavLink("Graphs", href="/page/Graphs")),
        dbc.NavItem(dbc.NavLink("Tables", href="/page/Tables")),
    ],
    brand="ECAT Reporting Tool",
    brand_href="#",
    fluid=True,
    sticky='top',
    color='primary',
    dark=True,
)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    html.Br(),
    # html.Div(id='page-content'),

    dcc.Dropdown(
        options=[{'label': str(c), 'value': str(c)} for c in reflist.Refinery],
        multi=True
    ),

    html.Br(),
    dcc.Dropdown(
        options=[{'label': str(c), 'value': str(c)} for c in samptypelist],
        multi=False,
        searchable=False
    ),

    html.Br(),
    dcc.DatePickerRange(
            id='my-date-picker-range',
            min_date_allowed=date(1999, 1, 1),
            max_date_allowed=date.today(),
            initial_visible_month=date.today(),
            end_date=date.today(),
            updatemode='bothdates',
            stay_open_on_select=True,
            persistence=True,
            persisted_props=['start_date', 'end_date'],
            persistence_type='local',
        ),

    # DF Storage
    # dcc.Store(id='DFT-P', storage_type='memory'),
])

if __name__ == '__main__':
    app.run_server(debug=True)
