import dash
import dash_daq as daq
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash_extensions import Download
from dash_extensions.snippets import send_data_frame
import plotly.express as px
import plotly.graph_objects as go
import pyodbc
import pandas as pd
from datetime import date
from socket import gethostname
import time
import re
import statsmodels

from app import app, server, cache, session_id

isHome = True if gethostname() == 'DESKTOP-G4MFTGK' else False

# region SQL Setup
sql_server = 'DESKTOP-G4MFTGK' if isHome else 'CDCSQLPROD01'
database = 'eCat'
trusted_cnxn = 'Yes'
cnxn = pyodbc.connect('TRUSTED_CONNECTION=' + trusted_cnxn + ';'
                      'DRIVER={SQL Server Native Client 11.0};'
                      'SERVER=' + sql_server + ';'
                      'DATABASE=' + database + ';'
                      )

q_units_string = """
                        SELECT DISTINCT Sub.REFINERY_ID, Sub.REFINERY_NAME
                        FROM (SELECT DISTINCT REFINERY_ID, REFINERY_NAME FROM eCat.dbo.Dry_Samples_vw
                        UNION ALL
                        SELECT DISTINCT REFINERY_ID, REFINERY_NAME FROM eCat.dbo.Liquid_Samples_vw) AS Sub
                        ORDER BY Sub.REFINERY_ID"""
q_units = pd.read_sql_query(q_units_string, cnxn)
q_units['Refinery'] = q_units['REFINERY_NAME'].astype(str) + ' (' + q_units['REFINERY_ID'].astype(str) + ')'
q_units_list = sorted(q_units['Refinery'].values.tolist())
q_sample_types_string = """
                        SELECT DISTINCT Sub.Sample_Type
                        FROM (SELECT DISTINCT Sample_Type FROM eCat.dbo.Dry_Samples_vw
                        UNION ALL
                        SELECT DISTINCT Sample_Type FROM eCat.dbo.Liquid_Samples_vw) AS Sub"""
q_sample_types = pd.read_sql(q_sample_types_string, cnxn)['Sample_Type'].values.tolist()
# endregion


# region Constants
graph_types = ['Scatter', 'Scatter_3D']
# endregion


# region Layout Objects
def control_tabs():
    """
    :return: A Div containing Intro, Query and Graphing Option tabs
    """
    return html.Div(
        id='ecat-control-tabs',
        children=[
            dcc.Tabs(id='ecat-tabs', value='what-is', children=[
                dcc.Tab(
                    label='About',
                    value='what-is',
                    children=html.Div(children=[
                        html.H4(children='Purpose?'),
                        html.P('ECAT Reporting Tool is a visualizer that allows you to explore ECAT data '
                               'in multiple representations.'),
                        html.P('You can query by sample type, refinery, and date ranges '),
                        html.P('Version 0.4 - 10/28/20'),
                        dcc.Markdown("""Author: [Yupei Chen](mailto:Yupei.Chen@Albemarle.com)""")
                    ])
                ),
                dcc.Tab(
                    label='Database Query',
                    value='query',
                    children=html.Div(children=[
                        html.Div(
                            id='query-card', children=[
                                html.Br(),
                                html.Div([
                                    html.Div(html.P(id='benchmark-text', children=['Benchmarking OFF']),
                                             style={'display': 'inline-block', 'marginRight': 40}),
                                    html.Div(
                                        daq.ToggleSwitch(
                                            id='benchmark-toggle',
                                            value=False,
                                        ), style={'display': 'inline-block'}
                                    ),
                                ]),
                                html.Br(),
                                html.P('Select Sample Type'),
                                dcc.Dropdown(
                                    id='sample-type-select',
                                    # ECAT_LO disabled, confidential data
                                    options=[{'label': str(c), 'value': str(c), 'disabled': True if c == 'ECAT_LO' else False} for c in q_sample_types],
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
                                html.Div(id='refinery-div', children=[
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
                                ]),
                                html.Br(),
                                dbc.Button('Query ECAT DB', color='primary', id='query-button', n_clicks=0, className='mr-5'),
                                dbc.Button('Download CSV', color='info', id='dl-button', n_clicks=0, style=dict(display='none')),
                                Download(id='query-data-dl')
                            ]
                        )
                    ])
                ),
                dcc.Tab(
                    label='Graph Options',
                    value='graph-options',
                    children=html.Div(children=[
                        html.Div(
                            id='graph-card', children=[
                                html.Br(),
                                html.Div([
                                    dbc.Button('Data', color='primary', id='option-data-btn', className='mr-3'),
                                    dbc.Button('Analysis', color='primary', id='option-analysis-btn', className='mr-3'),
                                    dbc.Button('Customizations', color='primary', id='option-customization-btn', className='mr-3'),
                                    dbc.Button('Render Graphs', color='success', id='render-button', n_clicks=0)
                                ]),
                                dbc.Collapse(
                                    id='data-collapse', is_open=True, children=[
                                        html.Br(),
                                        html.P('Graph Type'),
                                        dcc.Dropdown(
                                            id='graph-type',
                                            options=[{'label': i, 'value': i} for i in graph_types],
                                            value=graph_types[0],
                                            searchable=False,
                                        ),
                                        html.Div(id='legend-div', children=[
                                            html.Br(),
                                            html.P('Legend'),
                                            dcc.Dropdown(
                                                id='legend-col',
                                                options=[{'label': i, 'value': i} for i in
                                                         ['Refinery_Name', 'Current_Catalyst']],
                                                value='Refinery_Name',
                                                searchable=False,
                                            ),
                                        ]),
                                        html.Div(id='highlight-div', children=[
                                            html.Br(),
                                            html.P('Highlight'),
                                            dcc.Dropdown(
                                                id='highlight-select',
                                                options=[{'label': str(c), 'value': str(c)} for c in q_units_list],
                                                multi=True,
                                                persistence=True,
                                                persisted_props=['value'],
                                                persistence_type='local',
                                            ),
                                        ]),
                                        html.Div(id='axis-selectors', children=[
                                            html.Br(),
                                            html.P('X-Axis', id='x-text'),
                                            dcc.Dropdown(id='x-col'),
                                            html.Br(),
                                            html.P('Y-Axis', id='y-text'),
                                            dcc.Dropdown(id='y-col'),
                                            html.Br(),
                                            html.P('Z-Axis', id='z-text'),
                                            dcc.Dropdown(id='z-col'),
                                        ]),
                                    ]
                                ),
                                dbc.Collapse(
                                    id='analysis-collapse', is_open=False, children=[
                                        html.Br(),
                                        html.Div(id='trend-div', children=[
                                            html.Div(html.P('Trend Type'),
                                                     style={'display': 'inline-block', 'marginRight': 40}),
                                            html.Div(
                                                # daq.ToggleSwitch(
                                                #     id='trend-type',
                                                #     label='LOESS',
                                                #     value=False,
                                                #     labelPosition='bottom'
                                                # ),
                                                dcc.RadioItems(
                                                    id='trend-type',
                                                    options=[
                                                        {'label': 'OFF', 'value': 'OFF'},
                                                        {'label': 'LOESS', 'value': 'LOESS'},
                                                        {'label': 'OLS', 'value': 'OLS'}
                                                    ],
                                                    value='OFF',
                                                    labelStyle={'display': 'inline-block'},
                                                    inputStyle={"margin-left": "20px"}
                                                ),
                                                style={'display': 'inline-block'}
                                            ),
                                        ])
                                    ]
                                ),
                                dbc.Collapse(
                                    id='customization-collapse', is_open=False, children=[
                                        html.P('Insert Customizations Here')
                                    ]
                                )
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
        children=[
            dcc.Graph(
                id='custom-graph',
                figure={},
                style={'height': '80vh'}
            )
        ]
    )
# endregion


app.layout = dbc.Container(
    id='app-container', children=[
        # Banner
        html.Div(
            id='banner',
            className='banner',
            children=[html.Img(src=app.get_asset_url('plotly_logo.png'))]
        ),
        dbc.Row([
            dbc.Col(
                # Left Column
                html.Div(
                    id='left-column',
                    children=[
                        control_tabs(),
                        html.Br(),
                        dbc.Spinner(html.Div(id='query-msg')),
                        dbc.Spinner(html.Div(id='render-msg'))
                    ]
                ),
                width=3
            ),
            dbc.Col(
                # Right Column
                html.Div(
                    id='right-colulmn',
                    children=[
                        dcc.Markdown(id='debug'),
                        custom_graph(),
                    ]
                ), width=9
            ),
            # Column Storage
            dcc.Store(id='columns-memory', storage_type='memory'),
        ])
    ]
)


# region Callbacks
@app.callback(
    Output('render-msg', 'children'),
    [Input('render-button', 'n_clicks')]
)
def render_msg(n_clicks):
    if n_clicks < 1:
        raise PreventUpdate
    alert_msg = f"Rendering your visualization..."
    alert = dbc.Alert(alert_msg, color='warning', dismissable=True, duration=2000)
    return alert


@app.callback(
    [
        Output('query-msg', 'children'),
        Output('columns-memory', 'data'),
        Output('dl-button', 'style'),
    ],
    [Input('query-button', 'n_clicks')],
    [
        State('sample-type-select', 'value'),
        State('date-picker-select', 'start_date'),
        State('date-picker-select', 'end_date'),
        State('refinery-select', 'value'),
        State('benchmark-toggle', 'value')
    ]
)
def query(n_clicks, sample_type, sdate, edate, refinery, benchmark_toggle):
    # TODO: Try block to validate query returns data, return error as alert
    if n_clicks < 1:
        raise PreventUpdate
    t0 = time.time()
    params = [sample_type, sdate, edate]

    # Base SQL Statement
    q_string = """Select *
                        FROM dbo.Dry_Samples_vw
                        WHERE Sample_Type = {0} 
                        AND Sample_Date BETWEEN {0} and {0}"""
    q_string = q_string.format('?')
    if sample_type in ['WGS', 'SLURRY FINES 1', 'FEED']:
        q_string = q_string.replace('dbo.Dry_Samples_vw', 'dbo.Liquid_Samples_vw')

    # Modification for Benchmarking
    if not benchmark_toggle:
        refinery_list = q_units[q_units.Refinery.isin(refinery)]
        refinery_list = refinery_list['REFINERY_ID'].tolist()
        params += refinery_list
        q_string += ' AND Refinery_ID IN ({0})'
        q_string = q_string.format(','.join('?' * len(refinery_list)))

    # Read SQL
    df = pd.read_sql_query(q_string, cnxn, params=params, parse_dates=['Sample_Date'])

    # Post-Read Format
    df.dropna(axis='columns', how='all', inplace=True)

    # Columns Setup
    columns = df.columns.tolist()
    col_to_remove = ['Sample_Number', 'Arrival_Date', 'Refinery_ID', 'Sampling_Point', 'Sample_Type', 'Comment', 'ECAT_Original_ID']
    col_to_remove += ['SF_Account_ID', 'Current_Catalyst', 'Current_Supplier', 'Refinery_Name', 'Sample_Year', 'Create_Date', 'Update_Date']
    columns = [i for i in columns if i not in col_to_remove]

    # Cache Data
    cache.set(session_id, df)

    t1 = time.time()
    exec_time = t1-t0
    query_size = df.shape[0]
    alert_msg = f"Queried {query_size} records. Total time: {exec_time:.2f}s."
    alert = dbc.Alert(alert_msg, color='success', dismissable=True, duration=2000)
    return alert, columns, dict()


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
        Output('z-col', 'style'),
        Output('z-text', 'style')
    ],
    [Input('graph-type', 'value')]
)
def update_data_options(g_type):
    if g_type == 'Scatter_3D':
        return dict(), dict()
    else:
        return dict(display='none'), dict(display='none')


@app.callback(
    [
        Output('refinery-div', 'style'),
        Output('legend-div', 'style'),
        Output('highlight-div', 'style'),
    ],
    [Input('benchmark-toggle', 'value')]
)
def update_data_options(benchmark_toggle):
    s = dict()
    h = dict(display='none')
    if not benchmark_toggle:
        return s, s, h
    else:
        return h, h, s


# @app.callback(
#     Output('trend-type', 'label'),
#     [Input('trend-type', 'value')]
# )
# def update_trend_label(value):
#     if value:
#         return 'OLS'
#     else:
#         return 'LOESS'


@app.callback(
    [
        Output('benchmark-text', 'children'),
        Output('trend-div', 'style')
    ],
    [Input('benchmark-toggle', 'value')]
)
def update_benchmark_text(value):
    if value:
        return ['Benchmarking ON'], dict(display='none')
    else:
        return ['Benchmarking OFF'], dict()


@app.callback(
    Output('custom-graph', 'figure'),
    [Input('render-button', 'n_clicks')],
    [
        State('x-col', 'value'),
        State('y-col', 'value'),
        State('z-col', 'value'),
        State('benchmark-toggle', 'value'),
        State('graph-type', 'value'),
        State('legend-col', 'value'),
        State('highlight-select', 'value'),
        State('trend-type', 'value')
    ]
)
def render_graph(n_clicks, x, y, z, benchmark_toggle, graph_type, legend, selects, trend_type):
    if n_clicks < 1:
        raise PreventUpdate
    df = cache.get(session_id)
    if df is None:
        # TODO: Alert to user that there is no data to render
        raise PreventUpdate
    else:
        if benchmark_toggle:
            # Benchmark Plot using ScatterGL for increased speed
            # Regex looks for any number of digits between parenthesis
            refinery_id_list = list(map(lambda select: re.search(r"(?<=\()\d+(?=\))", select).group(0), selects))
            trace_benchmark = go.Scattergl(x=df[x], y=df[y], name='Industry Standard', mode='markers', marker=dict(opacity=0.3))
            data = [trace_benchmark]
            for index, refinery in enumerate(refinery_id_list):
                df2 = df[df.Refinery_ID.eq(refinery)]
                trace_target = go.Scattergl(x=df2[x], y=df2[y], name=selects[index], mode='markers', marker=dict(size=10,
                                                                                                                 line=dict(width=2,
                                                                                                                           color='DarkSlateGrey')))
                data.append(trace_target)
            layout = go.Layout(title='Benchmarking Plot', xaxis_title=x, yaxis_title=y)
            fig = go.Figure(data=data, layout=layout)
        else:
            if graph_type == 'Scatter':
                fig = px.scatter(df, x=x, y=y, color=legend, trendline='ols' if trend_type else 'lowess')
            elif graph_type == 'Scatter_3D':
                fig = px.scatter_3d(df, x=x, y=y, z=z, color=legend)
        fig.update_layout(legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ))
        return fig


@app.callback(
    Output('query-data-dl', 'data'),
    [Input('dl-button', 'n_clicks')]
)
def generate_csv(n_clicks):
    if n_clicks < 1:
        raise PreventUpdate
    df = cache.get(session_id)
    if df is None:
        raise PreventUpdate
    else:
        return send_data_frame(df.to_csv, filename='querydata.csv')


@app.callback(
    [
        Output('data-collapse', 'is_open'),
        Output('analysis-collapse', 'is_open'),
        Output('customization-collapse', 'is_open')
    ],
    [
        Input('option-data-btn', 'n_clicks'),
        Input('option-analysis-btn', 'n_clicks'),
        Input('option-customization-btn', 'n_clicks')
    ],
    [
        State('data-collapse', 'is_open'),
        State('analysis-collapse', 'is_open'),
        State('customization-collapse', 'is_open')
    ]
)
def toggle_collapse(d_click, a_click, c_click, d_state, a_state, c_state):
    ctx = dash.callback_context
    if not ctx.triggered:
        return False, False, False
    else:
        btn_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if btn_id == 'option-data-btn' and d_click:
        return not d_state, False, False
    elif btn_id == 'option-analysis-btn' and a_click:
        return False, not a_state, False
    elif btn_id == 'option-customization-btn' and c_click:
        return False, False, not c_state
    return False, False, False
# endregion


if __name__ == '__main__':
    app.run_server(debug=True)
