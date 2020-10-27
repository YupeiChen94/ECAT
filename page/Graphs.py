import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.express as px
from datetime import date

from app import app
# from page.Options import col_DFT_p, col_DFT_f, col_HR_p, col_HR_a, col_HR_d

# region Constants

# endregion

# region Styling
# tab_style = {
#     'borderBottom': '1px solid #d6d6d6',
#     'padding': '6px',
#     'fontWeight': 'bold'
# }
# tab_selected_style = {
#     'borderTop': '1px solid #d6d6d6',
#     'borderBottom': '1px solid #d6d6d6',
#     'backgroundColor': '#119DFF',
#     'color': 'white',
#     'padding': '6px'
# }
# dft_colors = {
#     'background': ''
# }
# endregion


# region Functions
# endregion


# region Objects

# def create_controls(col_list):
#     plot_controls = dbc.Card(
#         [
#             dbc.FormGroup(
#                 [
#                     dbc.Label('X-Axis'),
#                     dcc.Dropdown(
#                         id='x-col',
#                         # options=[{'label': i, 'value': i} for i in col_list],
#                         options=[{'label': col_list[0], 'value': col_list[0]}],
#                         value=col_list[0],
#                         searchable=False,
#                         disabled=True
#                     ),
#                     dcc.RadioItems(
#                         id='x-type',
#                         options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
#                         value='Linear',
#                         labelStyle={'margin-right': '10px'}
#                     )
#                 ],
#             ),
#             dbc.FormGroup(
#                 [
#                     dbc.Label('Y-Axis'),
#                     dcc.Dropdown(
#                         id='y-col',
#                         options=[{'label': i, 'value': i} for i in col_list[1:]],
#                         value=col_list[1],
#                         searchable=False
#                     ),
#                     dcc.RadioItems(
#                         id='y-type',
#                         options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
#                         value='Linear',
#                         labelStyle={'margin-right': '10px'}
#                     )
#                 ],
#             ),
#         ],
#         body=True,
#         style={
#                 'borderBottom': 'thin lightgrey solid',
#                 'backgroundColor': 'rgb(250,250,250)',
#                 'padding': '10px 10px'},
#     )
#     return plot_controls


# def create_plot():
#     graph_plot = dbc.Card(
#         [
#             # dbc.CardHeader('Plot Header'),
#             dcc.Graph(
#                 id='graph'
#             )
#         ]
#     )
#     return graph_plot
# endregion


layout = html.Div([
        # html.H3('Graphs'),
        # html.Br(),
        # dcc.Tabs(id='tabs', value='HR-P-tab', children=[
        #     dcc.Tab(label='DFT Pressure', value='DFT-P-tab', style=tab_style, selected_style=tab_selected_style),
        #     dcc.Tab(label='DFT Fitted', value='DFT-F-tab', style=tab_style, selected_style=tab_selected_style),
        #     dcc.Tab(label='HR Pressure', value='HR-P-tab', style=tab_style, selected_style=tab_selected_style),
        #     dcc.Tab(label='HR Adsorption', value='HR-A-tab', style=tab_style, selected_style=tab_selected_style),
        #     dcc.Tab(label='HR Desorption', value='HR-D-tab', style=tab_style, selected_style=tab_selected_style),
        # ], vertical=True, parent_style={'float': 'left'}),
        # dbc.Container([
        #     html.Div(id='graph-content')
        # ], fluid=True)
        control_tabs(),
    ],
    style={'padding': '20px'})


# region Callbacks
# @app.callback(
#     Output('graph-content', 'children'),
#     [Input('tabs', 'value')]
# )
# def render_graph_content(tab):
#     if tab is None:
#         raise PreventUpdate
#     controls = create_controls(get_column_list(tab))
#     plot = create_plot()
#     return html.Div([
#         dbc.Row(
#             [
#                 dbc.Col(controls, width=3),
#                 dbc.Col(plot, width=9)
#             ],
#         )
#     ])


# @app.callback(
#     Output('graph', 'figure'),
#     [
#         Input('tabs', 'value'),
#         Input('x-col', 'value'),
#         Input('y-col', 'value'),
#         Input('x-type', 'value'),
#         Input('y-type', 'value')
#     ],
#     [
#         State('DFT-P', 'data'),
#         State('DFT-F', 'data'),
#         State('HR-P', 'data'),
#         State('HR-A', 'data'),
#         State('HR-D', 'data')
#     ]
# )
# def create_graph(tab, x_col, y_col, x_type, y_type, dftp, dftf, hrp, hra, hrd):
#     if tab == 'DFT-P-tab':
#         table = dftp
#         col = col_DFT_p
#     elif tab == 'DFT-F-tab':
#         table = dftf
#         col = col_DFT_f
#     elif tab == 'HR-P-tab':
#         table = hrp
#         col = col_HR_p
#     elif tab == 'HR-A-tab':
#         table = hra
#         col = col_HR_a
#     elif tab == 'HR-D-tab':
#         table = hrd
#         col = col_HR_d
#     else:
#         raise PreventUpdate
#     if table is None:
#         raise PreventUpdate
#     if x_col not in col:
#         raise PreventUpdate
#     # fig = px.line(table, x=col[0], y=col[1], color='SID', height=800)
#     fig = px.line(table, x=x_col, y=y_col, color='SID', height=800)
#     fig.update_xaxes(title=x_col, type='linear' if x_type == 'Linear' else 'log')
#     fig.update_yaxes(title=y_col, type='linear' if y_type == 'Linear' else 'log')
#     return fig


# @app.callback(
#     Output('x-col', 'options'),
#     [Input('y-col', 'value')],
#     [State('tabs', 'value')],
#         )
# # Use to limit x axis selection
# def filter_options(v, tab):
#     return [{'label': i, 'value': i, 'disabled': i == v} for i in get_column_list(tab)]


# @app.callback(
#     Output('y-col', 'options'),
#     [Input('x-col', 'value')],
#     [State('tabs', 'value')]
# )
# # Use to limit y axis selection
# def filter_options(v, tab):
#     return [{'label': i, 'value': i, 'disabled': i == v} for i in get_column_list(tab)]

# endregion
