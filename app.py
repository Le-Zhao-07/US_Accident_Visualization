# -*- coding: utf-8 -*-
"""
Created on Fri Mar  6 14:10:16 2020

@author: zhaol
"""

import dash
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, 
                external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
app.config.suppress_callback_exceptions = True
