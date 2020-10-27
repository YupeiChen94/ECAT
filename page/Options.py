import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

from app import app

# # DFT
# col_DFT_v = ['Name', 'Value']
# col_DFT_p = ['Pore Diameter', 'Cum PV', 'Cum SA', 'dV/dlogD', 'dSA/dlogD']
# col_DFT_f = ['P/P0', 'Fitted V', 'Measured V']
#
# # HR
# col_HR_v = ['Name', 'Value']
# col_HR_p = ['Relative Pressure', 'Quantity Adsorbed']
# col_HR_a = ['PoreWidth-Abs-PoSD', 'PoSD_dV/dlog(D)PV-Abs']
# col_HR_d = ['PoreWidth-Des-PoSD', 'PoSD_dV/dlog(D)PV-Des']

layout = html.Div([
        html.H3('Options'),
    ],
    style={'padding': '20px'})