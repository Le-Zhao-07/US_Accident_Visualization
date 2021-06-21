# -*- coding: utf-8 -*-
"""
Created on Fri Mar  6 21:56:54 2020

@author: zhaol
"""

from app import app
import dash_bootstrap_components as dbc
import dash_html_components as html
from usmap import layout_mapfilter, layout_map, layout_search
from barchart import layout_barchart
from linechart import layout_linechart
from bubblechart import layout_bubblechart
from mlmodel import layout_mlmodel, layout_ratechart


# Feel free to change the layout as you need!

# 1. navbar
navbar = dbc.NavbarSimple(
    children=[
        dbc.DropdownMenu(
            nav=True,
            in_navbar=True,
            label="About",
            children=[
                dbc.DropdownMenuItem("Team"),
            ],
        ),
    ],
    brand="US Traffic Accident (2016-2019) Dashboard",
    sticky="top",
    dark=True,
    color="dark",
    fluid=True
)


body = dbc.Container([
    # header
     dbc.Row([
        dbc.Col(html.Div("US Traffic Accident (2016-2019) Dashboard")),
    ],
    style={
        "background-color": "#343a40",
        "color": "white",
        "font-size": "40px"
    }),

    # Map filter + Map
    dbc.Row([
        dbc.Col([layout_mapfilter, layout_search], width=3),
        dbc.Col([layout_map], width=9),
    ], style={"background-color": "#F0F0F0","margin-bottom":"50px"}),

    # ML model and accident rate per state
    # dbc.Row([
    #     dbc.Col([html.H4("Accident Severity Predictor", style={'text-align': 'center'})],width=12),
    #     dbc.Col([html.Div("Note: Select all the features on the left, the predictor will highlight the accident rate\
    #         (Number of Accidents / Number of Registered Cars of State * 100%)\
    #         of the selected state on the chart, and predict accident severity based on your input.\
    #         The range of accident severity is 1 ~ 4, in which 1 is minor, 4 is severe.",
    #          style={"font-size": "20px", "text-align":"center"})],width=12),
    # ], style={"background-color": "#F0F0F0"}),
    
    # dbc.Row([
    #     dbc.Col([layout_mlmodel], width=4),
    #     dbc.Col([layout_ratechart], width=8),
    # ], style={"background-color": "#F0F0F0","margin-bottom":"50px"}),

    # bar chart
    dbc.Row([
        dbc.Col([layout_barchart], width=12),
    ], style={"background-color": "#F0F0F0","margin-bottom":"50px"}),

    # line chart
    dbc.Row([
        dbc.Col([layout_linechart], width=12),
    ], style={"background-color": "#F0F0F0","margin-bottom":"50px"}),    

    # bubble chart
    dbc.Row([
        dbc.Col([layout_bubblechart], width=12),
    ], style={"background-color":"#F0F0F0","margin-bottom":"50px"})
    
],
style={"background-color": "#d9d9d9"},
fluid=True)

app.layout = html.Div([body])

if __name__ == '__main__':
    app.run_server(debug=False, host="0.0.0.0", port=8080)