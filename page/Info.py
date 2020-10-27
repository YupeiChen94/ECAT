import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from app import app

# Markdown text
markdown_text_basic = '''
### ECAT Reporting Tool

Version
0.1

Date:
10/12/2020

Author: [Yupei Chen](mailto:Yupei.Chen@Albemarle.com)  
'''

markdown_text_todo = '''
#### ToDo: 
Adapt Upload Page/Rename to Query
Adapt Table Page
Adapt Graph Page

Customization
'''

markdown_text_done = '''
#### Done:
Migrate boilerplate code
'''


layout = html.Div([
    dbc.Row([
        # Basic
        dbc.Col(dcc.Markdown(markdown_text_basic)),
        # Do List
        dbc.Col(dcc.Markdown(markdown_text_todo)),
        # Done
        dbc.Col(dcc.Markdown(markdown_text_done))
        ]),
    ],
    style={'padding': '20px'})

