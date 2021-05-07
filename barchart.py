# -*- coding: utf-8 -*-
"""
Created on Fri Mar  6 15:02:33 2020

@author: zhaol
"""

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from database import executeSQL
import numpy as np
from app import app


state_cnt_SQL = """SELECT State, SUM(cnt) AS cnt 
        FROM barchart
        GROUP BY State
        ORDER BY cnt DESC"""
state_cnt_df = executeSQL(state_cnt_SQL)



def generate_barchart(df=state_cnt_df, x_column='State', xaxis_title='State'):
    return {
        'data': [
            dict(
                x=df[x_column],
                y=df['cnt'],
                type='bar'
            ) 
        ],
        'layout': dict(
            xaxis={'title': xaxis_title,'tickvals': df[x_column]},
            yaxis={'title': 'Number of Accidents'},
            margin={'l': 100, 'b': 100, 't': 50, 'r': 80},
            hovermode='closest',
            font=dict(size=15),
        )
    }

barchart_names = ['State','Severity','Weather']
select_years = ['2016-2019 total','2016','2017','2018','2019']
barchart_severity = ['All Severities','1','2','3','4']
barchart_side = ['Both Sides','L','R']
barchart_weather = ['All Weather Conditions','Cloudy','Clear','Rain','Haze','Snow','Fog']

layout_barchart = html.Div([
    html.H5(children = "", id="bar_header1", style={'text-align': 'center'}),
    html.H6(children = "",id="bar_header2", style={'text-align': 'center'}),

    html.Div([
        html.Label("X-axis", className='label'),
        html.Div([
            dcc.Dropdown(
                id='bar_names',
                options=[{'label': i, 'value': i} for i in barchart_names],
                value='State'
            )
        ],
        style={'width': '75%', 'display': 'inline-block', 'verticalAlign':'middle'}),       
    ],
    style={'width':'25%', 'display': 'inline-block', 'verticalAlign':'middle'}),

    html.Div([
        html.Label("Filters", className='label'),

        html.Div([
            dcc.Dropdown(
                id='bar_select_year',
                options=[{'label': i, 'value': i} for i in select_years],
                value='2016-2019 total'
            )
        ],
        style={'width': '20%','display': 'inline-block', 'verticalAlign':'middle'}),

        html.Div([ 

            dcc.Dropdown(
                id = 'bar_severity',
                options=[{'label': i, 'value': i} for i in barchart_severity],
                value='All Severities'
            ),  
        ],
        style={'width': '20%', 'display': 'inline-block', 'verticalAlign':'middle'}),

        html.Div([ 

            dcc.Dropdown(
                id = 'bar_side',
                options=[{'label': i, 'value': i} for i in barchart_side],
                value='Both Sides'
            ),  
        ],
        style={'width': '20%', 'display': 'inline-block', 'verticalAlign':'middle'}),

        html.Div([ 
            dcc.Dropdown(
                id = 'bar_weat',
                options=[{'label': i, 'value': i} for i in barchart_weather],
                value='All Weather Conditions'
            ), 
        ],
        style={'width': '20%', 'display': 'inline-block', 'verticalAlign':'middle'}),
    ],
    style={'width':'75%', 'display': 'inline-block', 'verticalAlign':'middle'}),

    dcc.Graph(
        id='bar_figure',
        figure=generate_barchart(),
        style={"height": "70vh"}
    )
])

def generate_where_clause(select_year, bar_sever, bar_side, bar_weat):
    where_clauses = []
    if select_year != '2016-2019 total': 
        where_clauses.append('year = "' + select_year  + '" ') 
    if bar_sever != 'All Severities': 
        where_clauses.append('Severity = '+ str(bar_sever) + ' ')
    if bar_side !='Both Sides':
        where_clauses.append('Side = "'+ bar_side + '" ')
    if bar_weat != 'All Weather Conditions':
        where_clauses.append('Weather_Condition = "' + bar_weat  + '" ')

    return " AND ".join(where_clauses)


# call back
@app.callback(
   [Output('bar_figure', 'figure'),
   Output('bar_header1','children'),
   Output('bar_header2','children')],
    [Input('bar_names', 'value'),
    Input('bar_select_year', 'value'),
    Input('bar_severity', 'value'),
    Input('bar_side', 'value'),
    Input('bar_weat', 'value')]) 

def update_bar_graph (xaxis,fg_year,fg_sever,fg_side,fg_weat):
    bar_names = xaxis
    select_year = fg_year
    bar_sever = fg_sever
    bar_side = fg_side
    bar_weat = fg_weat

    header2= "(year: {},   accident severity: {},   road side: {},   weather: {})".format(select_year, bar_sever, bar_side, bar_weat)

    #State_count
    if bar_names == 'State':

        header1 = "Number of Accidents vs. State" 

        where_clause = generate_where_clause(select_year, bar_sever, bar_side, bar_weat)

        if where_clause == "":
            state_SQL = """SELECT State, SUM(cnt) AS cnt 
                        FROM barchart 
                        GROUP BY State
                        ORDER BY cnt DESC"""
        else:
            state_SQL = """SELECT State, SUM(cnt) AS cnt 
                        FROM barchart
                        WHERE {} 
                        GROUP BY State
                        ORDER BY cnt DESC""".format(where_clause)

        state_df = executeSQL(state_SQL)

        return  generate_barchart(df=state_df, x_column='State', xaxis_title='State'), header1, header2

    #Severity count
    elif bar_names == 'Severity':

        header1 = "Number of Accidents vs. Severity"

        where_clause = generate_where_clause(select_year, bar_sever, bar_side, bar_weat)

        if where_clause == "":
            severity_SQL = """SELECT Severity, SUM(cnt) AS cnt 
                        FROM barchart 
                        GROUP BY Severity"""
        else:
            severity_SQL = """SELECT Severity, SUM(cnt) AS cnt 
                        FROM barchart 
                        WHERE {}
                        GROUP BY Severity""".format(where_clause)

        severity_df = executeSQL(severity_SQL)

        return generate_barchart(df=severity_df, x_column='Severity', xaxis_title='Severity'), header1, header2

    
    #Weather count
    elif bar_names == 'Weather':

        header1 = "Number of Accidents vs. Weather Condition"

        where_clause = generate_where_clause(select_year, bar_sever, bar_side, bar_weat)
        
        if where_clause == "":
            weather_SQL = """SELECT Weather_Condition, SUM(cnt) AS cnt 
                        FROM barchart
                        WHERE Weather_Condition NOT NULL AND Weather_Condition != ""
                        GROUP BY Weather_Condition                       
                        ORDER BY cnt DESC
                        LIMIT 7"""
        else:
            weather_SQL = """SELECT Weather_Condition, SUM(cnt) AS cnt 
                        FROM barchart
                        WHERE Weather_Condition NOT NULL AND Weather_Condition != "" AND {} 
                        GROUP BY Weather_Condition
                        ORDER BY cnt DESC
                        LIMIT 7""".format(where_clause)

        weather_df = executeSQL(weather_SQL)

        return generate_barchart(df=weather_df, x_column='Weather_Condition', xaxis_title='Weather Condition'), header1, header2

