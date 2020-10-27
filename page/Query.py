import dash_table
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import re
import pandas as pd
import glob
import shutil

from app import app
# from page.Options import col_DFT_p, col_DFT_f, col_DFT_v, col_HR_p, col_HR_a, col_HR_d, col_HR_v

# region Constants
# directory = 'C:/Users/flute/PycharmProjects/ALB/ECAT/Resources/Input/'
# endregion


# region Functions
# endregion


# region Initialization
# endregion

layout = html.Div([
        html.H3('Query'),
        html.Br(),
        dbc.Card(
            [
                html.Button(children='Generate Data', id='btn-generate', n_clicks=0),
                html.Div(children='', id='text-generate')
            ])
    ],
    style={'padding': '20px'})


# region Callbacks
@app.callback(
    [
        Output('text-generate', 'children'),
        Output('DFT-P', 'data'),
        Output('DFT-F', 'data'),
        Output('DFT-V', 'data'),
        Output('HR-P', 'data'),
        Output('HR-A', 'data'),
        Output('HR-D', 'data'),
        Output('HR-V', 'data')
    ],
    [Input('btn-generate', 'n_clicks')],
    [State('sid-selector-table', 'derived_virtual_selected_row_ids')]
)
def update_upload_status(n_clicks, selected_row_ids):
    if n_clicks < 1:
        raise PreventUpdate
    else:
        if not selected_row_ids:
            raise PreventUpdate
        else:
            master_dft_p, master_dft_f, master_dft_v, master_hr_p, master_hr_a, master_hr_d, master_hr_v = read_csvs(selected_row_ids)
            return 'Data generated for selected sample(s): {}'.format(selected_row_ids), master_dft_p, master_dft_f, master_dft_v, master_hr_p, master_hr_a, master_hr_d, master_hr_v
# endregion
