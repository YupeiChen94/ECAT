import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, ClientsideFunction
from dash.exceptions import PreventUpdate
import pyodbc
import pandas as pd
from datetime import date
import time

from app import app

# region SQL Setup
server = 'DESKTOP-G4MFTGK'
database = 'ALB'
trusted_cnxn = 'yes'
cnxn = pyodbc.connect('DRIVER={SQL Server};'
                      'SERVER='+server+';'
                      'DATABASE='+database+';'
                      'TRUSTED_CONNECTION='+trusted_cnxn+';')

q_units_string = """
                        SELECT DISTINCT Sub.REFINERY_ID, Sub.REFINERY_NAME
                        FROM (SELECT DISTINCT REFINERY_ID, REFINERY_NAME FROM ALB.dbo.DrySamples
                        UNION ALL
                        SELECT DISTINCT REFINERY_ID, REFINERY_NAME FROM ALB.dbo.LiquidSamples) AS Sub
                        ORDER BY Sub.REFINERY_ID"""
q_units = pd.read_sql_query(q_units_string, cnxn)
q_units['Refinery'] = q_units['REFINERY_NAME'] + ' (' + q_units['REFINERY_ID'].astype(str) + ')'
q_units_list = q_units['Refinery'].values.tolist()
q_sample_types_string = """
                        SELECT DISTINCT Sub.Sample_Type
                        FROM (SELECT DISTINCT Sample_Type FROM ALB.dbo.DrySamples
                        UNION ALL
                        SELECT DISTINCT Sample_Type FROM ALB.dbo.LiquidSamples) AS Sub"""
q_sample_types = pd.read_sql(q_sample_types_string, cnxn)['Sample_Type'].values.tolist()
# endregion


# region Layout Objects
def control_tabs():
    """
    :return: A Div containing Intro and Graphing Option tabs
    """
    return html.Div(
        id='ecat-control-tabs',
        className='control-tabs',
        children=[
            dcc.Tabs(id='ecat-tabs', value='what-is', children=[
                dcc.Tab(
                    label='About',
                    value='what-is',
                    children=html.Div(className='control-tab', children=[
                        html.H4(className='what-is', children='Purpose?'),
                        html.P('ECAT Reporting Tool is a visualizer that allows you to explore ECAT data '
                               'in multiple representations.'),
                        html.P('You can query by sample type, refinery, and date ranges '),
                        html.P('Version 0.2 - 10/26/20'),
                        dcc.Markdown("""Author: [Yupei Chen](mailto:Yupei.Chen@Albemarle.com)""")
                    ])
                ),
                dcc.Tab(
                    label='Database Query',
                    value='query',
                    children=html.Div(className='control-tab', children=[
                        html.Div(
                            id='control-card', children=[
                                html.P('Select Sample Type'),
                                dcc.Dropdown(
                                    id='sample-type-select',
                                    options=[{'label': str(c), 'value': str(c)} for c in q_sample_types],
                                    multi=False,
                                    searchable=False,
                                    value=q_sample_types[0],
                                    persistence=True,
                                    persisted_props=['value'],
                                    persistence_type='local',
                                ),
                                html.Br(),
                                html.P('Select Date Range'),
                                dcc.DatePickerRange(
                                    id='date-picker-select',
                                    min_date_allowed=date(1999, 1, 1),
                                    max_date_allowed=date.today(),
                                    initial_visible_month=date.today(),
                                    end_date=date.today(),
                                    updatemode='singledate',
                                    stay_open_on_select=True,
                                    persistence=True,
                                    persisted_props=['start_date', 'end_date'],
                                    persistence_type='local',
                                ),
                                html.Br(),
                                html.Br(),
                                html.P('Select Refinery Unit(s)'),
                                dcc.Dropdown(
                                    id='refinery-select',
                                    options=[{'label': str(c), 'value': str(c)} for c in q_units_list],
                                    multi=True,
                                    persistence=True,
                                    persisted_props=['value'],
                                    persistence_type='local',
                                ),
                                html.Br(),
                                dbc.Button('Query ECAT DB', color='primary', id='query-button', n_clicks=0)
                            ]
                        )
                    ])
                )
            ])
        ]
    )
# endregion


# Multiple Units, Single SampleType, DateRange
# query_table = 'ALB.dbo.DrySamples'
# query_units = (540, 76)
# query_sample_type = 'ECAT'
# params = [query_sample_type]
# params += query_units

app.layout = html.Div(
    id='app-container', children=[
        # Banner
        html.Div(
            id='banner',
            className='banner',
            children=[html.Img(src=app.get_asset_url('plotly_logo.png'))]
        ),
        # Left Column
        html.Div(
            id='left-column',
            className='four columns',
            children=[control_tabs(), html.Br(), dbc.Spinner(html.Div(id='alert-msg'))]
            + [html.Div(['initial child'], id='output-clientside', style={'display': 'none'})]
        ),
        # Right Column
        html.Div(
            dcc.Markdown(id='debug'),
            # INSERT GRAPH HERE
        )

        # DF Storage
        # dcc.Store(id='DFT-P', storage_type='memory'),
    ])


@app.callback(
    [
        Output('alert-msg', 'children'),
        Output('debug', 'children')
    ],
    [Input('query-button', 'n_clicks')],
    [
        State('sample-type-select', 'value'),
        State('date-picker-select', 'start_date'),
        State('date-picker-select', 'end_date'),
        State('refinery-select', 'value')
    ]
)
def query(n_clicks, sample_type, sdate, edate, refinery):
    # TODO: Try block to validate query returns data
    if n_clicks < 1:
        raise PreventUpdate
    t0 = time.time()
    refinery_list = q_units[q_units.Refinery.isin(refinery)]
    refinery_list = refinery_list['REFINERY_ID'].tolist()
    params = [sample_type, sdate, edate]
    params += refinery_list

    # TODO: Modify table selection based on sample type
    # WGS, SLURRY FINES 1, FEED are LiquidSamples
    # TODO: Add an option for 'all' refinery units

    q_string = """Select Sample_Number, Refinery_ID, Sample_Type, Sample_Date
                        FROM dbo.DrySamples
                        WHERE Sample_Type = {0} 
                        AND Sample_Date BETWEEN {0} and {0}
                        AND Refinery_ID IN ({1})"""
    q_string = q_string.format('?', ','.join('?' * len(refinery_list)))
    df = pd.read_sql_query(q_string, cnxn, params=params)

    t1 = time.time()
    exec_time = t1-t0
    query_size = df.shape[0]
    alert_msg = f"Queried {query_size} records. Total time: {exec_time:.2f}s."
    alert = dbc.Alert(alert_msg, color='success', dismissable=True)
    return alert, 'None'

# @app.callback(Output('page-content', 'children'),
#               [Input('url', 'pathname')])
# def display_page(pathname):
#     if pathname == '/page/Information':
#         return Info.layout
#     elif pathname == '/page/Query':
#         return Query.layout
#     elif pathname == '/page/Options':
#         return Options.layout
#     elif pathname == '/page/Graphs':
#         return Graphs.layout
#     else:
#         return Info.layout


if __name__ == '__main__':
    app.run_server(debug=True)

    # Alternate Multi-page example
    # server.py
    # from flask import Flask
    #
    # server = Flask(__name__)
    #
    # app1.py
    # import dash
    # from server import server
    #
    # app = dash.Dash(name='app1', sharing=True, server=server, url_base_pathname='/app1')
    #
    # app2.py
    # import dash
    # from server import server
    #
    # app = dash.Dash(name='app2', sharing=True, server=server, url_base_pathname='/app2')
    #
    # run.py
    # from server import server
    # from app1 import app as app1
    # from app2 import app as app2
    #
    # if __name__ == '__main__':
    #     server.run()
