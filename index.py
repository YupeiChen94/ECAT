import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, ClientsideFunction
from dash.exceptions import PreventUpdate
import plotly.express as px
import pyodbc
import pandas as pd
from datetime import date
import time

from app import app, cache, session_id

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
    :return: A Div containing Intro, Query and Graphing Option tabs
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
                            id='query-card', children=[
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
                ),
                dcc.Tab(
                    label='Graph Options',
                    value='graph-options',
                    children=html.Div(className='control-tab', children=[
                        html.Div(
                            id='graph-card', children=[
                                html.P('X-Axis'),
                                dcc.Dropdown(
                                    id='x-col',
                                    options=[{'label': i, 'value': i} for i in ['xcollist']],
                                    # value='xcollist',
                                    searchable=True,
                                    disabled=False
                                ),
                                html.Br(),
                                html.P('Y-Axis'),
                                dcc.Dropdown(
                                    id='y-col',
                                    options=[{'label': i, 'value': i} for i in ['ycollist']],
                                    # value='ycollist',
                                    searchable=True,
                                    disabled=False
                                ),
                                html.Br(),
                                html.P('Z-Axis'),
                                dcc.Dropdown(
                                    id='z-col',
                                    options=[{'label': i, 'value': i} for i in ['zcollist']],
                                    # value='zcollist',
                                    searchable=True,
                                    disabled=False
                                ),
                                html.Br(),
                                dbc.Button('Render Graphs', color='primary', id='render-button', n_clicks=0)
                            ]
                        )
                    ])
                )
            ])
        ]
    )


def custom_graph():
    """
    :return: A Div containing the placeholder for a 2D or 3D graph visualization
    """
    return html.Div(
        id='custom-graph-div',
        className='graph-div',
        children=[
            dcc.Graph(
                id='custom-graph-2d',
                figure={},
                style={'height': '500px'}
            )
        ]
    )
# endregion


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
            id='right-colulmn',
            className='eight columns',
            children=[
                dcc.Markdown(id='debug'),
                custom_graph(),
            ]
        ),
        # Column Storage
        dcc.Store(id='columns-memory', storage_type='memory'),
    ])


@app.callback(
    [
        Output('alert-msg', 'children'),
        Output('columns-memory', 'data')
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
    # TODO: Try block to validate query returns data, return error as alert
    if n_clicks < 1:
        raise PreventUpdate
    t0 = time.time()
    refinery_list = q_units[q_units.Refinery.isin(refinery)]
    refinery_list = refinery_list['REFINERY_ID'].tolist()
    wet = True if sample_type in ['WGS', 'SLURRY FINES 1', 'FEED'] else False
    params = [sample_type, sdate, edate]
    params += refinery_list

    # TODO: Add an option for 'all' refinery units

    q_string = """Select *
                        FROM dbo.DrySamples
                        WHERE Sample_Type = {0} 
                        AND Sample_Date BETWEEN {0} and {0}
                        AND Refinery_ID IN ({1})"""
    if wet:
        q_string = q_string.replace('dbo.DrySamples', 'dbo.LiquidSamples')
    q_string = q_string.format('?', ','.join('?' * len(refinery_list)))
    df = pd.read_sql_query(q_string, cnxn, params=params)
    df.dropna(axis='columns', how='all', inplace=True)

    columns = df.columns.tolist()
    col_to_remove = ['Sample_Number', 'Sample_Date', 'Arrival_Date', 'Refinery_ID', 'Sampling_Point', 'Sample_Type', 'Comment', 'ECAT_Original_ID']
    col_to_remove += ['SF_Account_ID', 'Current_Catalyst', 'Current_Supplier', 'Refinery_Name', 'Sample_Year']
    columns = [i for i in columns if i not in col_to_remove]

    cache.set(session_id, df)

    t1 = time.time()
    exec_time = t1-t0
    query_size = df.shape[0]
    alert_msg = f"Queried {query_size} records. Total time: {exec_time:.2f}s."
    alert = dbc.Alert(alert_msg, color='success', dismissable=True, duration=2000)
    return alert, columns


@app.callback(
    [
        Output('x-col', 'options'),
        Output('y-col', 'options'),
        Output('z-col', 'options'),
    ],
    [
        Input('columns-memory', 'data'),
        Input('x-col', 'value'),
        Input('y-col', 'value'),
        Input('z-col', 'value')
    ]
)
def update_axis_selector(col_list, x, y, z):
    if col_list is None:
        raise PreventUpdate
    x_col = [{'label': i, 'value': i, 'disabled': i in [y, z]} for i in col_list]
    y_col = [{'label': i, 'value': i, 'disabled': i in [x, z]} for i in col_list]
    z_col = [{'label': i, 'value': i, 'disabled': i in [x, y]} for i in col_list]
    return x_col, y_col, z_col


@app.callback(
    [
        Output('custom-graph-2d', 'figure'),
        Output('debug', 'children')
    ],
    [
        Input('render-button', 'n_clicks')
    ]
)
def render_graph(n_clicks):
    if n_clicks < 1:
        raise PreventUpdate
    df = cache.get(session_id)
    if df is None:
        # TODO: Alert to user that there is no data to render
        raise PreventUpdate
    else:
        # TODO: Trendline option?
        fig = px.scatter(df, x='MPSD', y='Sb_PPM', color='Refinery_Name')
        return fig, ['']
    # return ['']


if __name__ == '__main__':
    app.run_server(debug=True)
