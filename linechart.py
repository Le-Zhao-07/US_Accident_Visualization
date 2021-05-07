# -*- coding: utf-8 -*-
"""
Created on Fri Mar  6 15:17:51 2020

@author: zhaol
"""

import dash_core_components as dcc
import dash_html_components as html
from app import app
from dash.dependencies import Input, Output
from database import executeSQL
import numpy as np



# Query of initial data
sev_y = """SELECT year, SUM(count) AS count
        FROM linechart_count_by_year
        GROUP BY year"""
sev_y_df = executeSQL(sev_y)

###############################################################################

def generate_linechart(df=sev_y_df, x_column='year', xaxis_title='Year'):
    return {
            "data": [{
                "x": df[x_column], 
                "y": df['count'],
                "mode": "markers+lines"
            }],
            'layout': dict(
                xaxis={'title': xaxis_title,'tickvals': df[x_column]},
                yaxis={'title': 'Number of Accidents'},
                margin={'l': 100, 'b': 150, 't': 50, 'r': 80},
                hovermode='closest',
                font=dict(size=15),
            )
        }
linechart_xaxis = ['Year', 'Year-Month', 'Month', 'Day of the Week', 'Time of the Day']
linechart_severity = ['All Severities','1','2','3','4']
linechart_side = ['Both Sides','L','R']
linechart_weather = ['All Weather Conditions','Cloudy','Clear','Rain','Haze','Snow','Fog']

layout_linechart = html.Div([        
    html.H5(children = "", id="line_header1", style={'text-align': 'center'}),
    html.H6(children = "",id="line_header2", style={'text-align': 'center'}),

    html.Div([
        html.Label("X-axis", className='label'),
        html.Div([
            dcc.Dropdown(
                id='yr_or_t',
                options=[{'label': i, 'value': i} for i in linechart_xaxis],
                value='Year'
            ),
        ],
        style={'width': '75%', 'display': 'inline-block', 'verticalAlign':'middle'}),       
    ],
    style={'width':'25%', 'display': 'inline-block', 'verticalAlign':'middle'}),

    html.Div([
        html.Label("Filters", className='label'),
        html.Div([         
            dcc.Dropdown(
                id = 'sev',
                options=[{'label': i, 'value': i} for i in linechart_severity],
                value='All Severities'
            ),  
        ],
        style={'width': '20%', 'display': 'inline-block', 'verticalAlign':'middle'}),

        html.Div([ 
            dcc.Dropdown(
                id='side',
                options=[{'label': i, 'value': i} for i in linechart_side],
                value='Both Sides'
            ),
        ],
        style={'width': '20%', 'display': 'inline-block', 'verticalAlign':'middle'}),
                
        html.Div([ 
            dcc.Dropdown(
                id = 'wea',
                options=[{'label': i, 'value': i} for i in linechart_weather],
                value='All Weather Conditions'
            ), 
        ],
        style={'width': '20%', 'display': 'inline-block', 'verticalAlign':'middle'}),  
    ],
    style={'width':'75%', 'display': 'inline-block', 'verticalAlign':'middle'}),
               
    dcc.Graph(
        id = 'linechart',
        figure=generate_linechart(),
        style={"height": "70vh"}
    ),
])

def generate_where_clause(severity, side, weather):
    where_clauses = []
    if severity != 'All Severities': 
        where_clauses.append('Severity = '+ str(severity) + ' ') 
    if side !='Both Sides': 
        where_clauses.append('Side = "'+ side + '" ')
    if weather != 'All Weather Conditions':
        where_clauses.append('Weather_Condition = "' + weather  + '" ')

    return " AND ".join(where_clauses)  

# =============================================================================
@app.callback(
    [Output('linechart', 'figure'),
    Output('line_header1','children'),
    Output('line_header2','children')],
    [Input('yr_or_t', 'value'),
     Input('sev', 'value'),
     Input('side', 'value'),
     Input('wea', 'value')])
def update_graph(xaxis, ft_sev, ft_side, ft_wea):

    yr_or_t = xaxis
    severity = ft_sev
    side = ft_side
    weather = ft_wea

    header2= "(accident severity: {},   road side: {},   weather: {})".format(severity, side, weather)

    # Update Year data
    if yr_or_t == 'Year':

        header1 = "Number of Accidents vs. Year"

        where_clause = generate_where_clause(severity, side, weather)

        if where_clause == "":
            data_y = """SELECT year, SUM(count) AS count 
                    FROM linechart_count_by_year
                    GROUP BY year"""
        else:
            data_y = """SELECT year, SUM(count) AS count 
                    FROM linechart_count_by_year
                    WHERE {}
                    GROUP BY year""".format(where_clause)
    
        data_y_df = executeSQL(data_y)

        return generate_linechart(df=data_y_df, x_column='year', xaxis_title='Year'), header1, header2

    # update Year Month data
    elif yr_or_t == "Year-Month":

        header1 = "Number of Accidents vs. Year-Month"

        where_clause = generate_where_clause(severity, side, weather)

        if where_clause == "":
            data_ym = """SELECT year_month, SUM(count) AS count 
                    FROM linechart_count_by_year_month
                    GROUP BY year_month"""
        else:
            data_ym = """SELECT year_month, SUM(count) AS count 
                    FROM linechart_count_by_year_month
                    WHERE {}
                    GROUP BY year_month""".format(where_clause)

        data_ym_df = executeSQL(data_ym)

        return generate_linechart(df=data_ym_df, x_column='year_month', xaxis_title='Year-Month'), header1, header2

    # update Month data
    elif yr_or_t == "Month":

        header1 = "Number of Accidents vs. Month"

        where_clause = generate_where_clause(severity, side, weather)

        if where_clause == "":
            data_m = """SELECT month, SUM(count) AS count 
                    FROM linechart_count_by_month
                    GROUP BY month"""
        else:
            data_m = """SELECT month, SUM(count) AS count 
                    FROM linechart_count_by_month
                    WHERE {}
                    GROUP BY month""".format(where_clause)

        data_m_df = executeSQL(data_m)

        return generate_linechart(df=data_m_df, x_column='month', xaxis_title='Month'), header1, header2


    # update day of the week data
    elif yr_or_t == "Day of the Week":

        header1 = "Number of Accidents vs. Day of the Week"

        where_clause = generate_where_clause(severity, side, weather)

        if where_clause == "":
            data_m = """SELECT week, SUM(count) AS count 
                    FROM linechart_count_by_week
                    GROUP BY week
                    ORDER BY
                        CASE week    
                            WHEN 'Mon' THEN 0
                            WHEN 'Tue' THEN 1
                            WHEN 'Wed' THEN 2
                            WHEN 'Thu' THEN 3
                            WHEN 'Fri' THEN 4
                            WHEN 'Sat' THEN 5
                            WHEN 'Sun' THEN 6     
                        END"""
        else:
            data_m = """SELECT week, SUM(count) AS count 
                    FROM linechart_count_by_week
                    WHERE {}
                    GROUP BY week
                    ORDER BY
                        CASE week
                            WHEN 'Mon' THEN 0
                            WHEN 'Tue' THEN 1
                            WHEN 'Wed' THEN 2
                            WHEN 'Thu' THEN 3
                            WHEN 'Fri' THEN 4
                            WHEN 'Sat' THEN 5
                            WHEN 'Sun' THEN 6        
                        END""".format(where_clause)

        data_m_df = executeSQL(data_m)

        return generate_linechart(df=data_m_df, x_column='week', xaxis_title='Day of the Week'), header1, header2

    
    # Update time of the day data        
    elif yr_or_t == 'Time of the Day':

        header1 = "Number of Accidents vs. Time of the Day"

        where_clause = generate_where_clause(severity, side, weather)

        if where_clause == "":
            data_t = """SELECT hour_of_day, SUM(count) AS count 
                    FROM linechart_count_by_time
                    GROUP BY hour_of_day"""
        else:
            data_t = """SELECT hour_of_day, SUM(count) AS count 
                    FROM linechart_count_by_time
                    WHERE {}
                    GROUP BY hour_of_day""".format(where_clause)
    
        data_t_df = executeSQL(data_t)

        return generate_linechart(df=data_t_df, x_column='hour_of_day', xaxis_title='Time of the Day (hour)'), header1, header2
    


# =============================================================================