# -*- coding: utf-8 -*-
"""
Created on Fri Mar  6 22:53:07 2020

@author: Rui Hu/Le Zhao
"""
#%%
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import pandas as pd
from database import locationsOnMap, executeSQL
import numpy as np
from dash.dependencies import Input, Output
from app import app
import itertools

vis_time_SQL = "SELECT * FROM count_sev_by_vis_time"
vis_time_df = executeSQL(vis_time_SQL)
vis_time_df['tooltip'] = "Count: " + vis_time_df['count'].astype(str) + "<br>" + vis_time_df['avg_severity'].apply(lambda x: f"Mean Severity: {x:.2f}")

vis_time_total_SQL = """SELECT vis, hour_of_day, SUM(count) AS count, AVG(avg_severity) AS avg_severity 
                        FROM count_sev_by_vis_time
                        GROUP BY vis, hour_of_day
                        ORDER BY
                            CASE vis
                                WHEN '[0,2)' THEN 0
                                WHEN '[2,5)' THEN 1
                                WHEN '[5,10)' THEN 2
                                WHEN 'over 10' THEN 3
                            END;"""
vis_time_total_df = executeSQL(vis_time_total_SQL)
vis_time_total_df['tooltip'] = "Count: " + vis_time_total_df['count'].astype(str) + "<br>" + vis_time_total_df['avg_severity'].apply(lambda x: f"Mean Severity: {x:.2f}")



temp_time_SQL = "SELECT * FROM count_sev_by_temp_time"
temp_time_df = executeSQL(temp_time_SQL)
temp_time_df['tooltip'] = "Count: " + temp_time_df['count'].astype(str) + "<br>" + temp_time_df['avg_severity'].apply(lambda x: f"Mean Severity: {x:.2f}")

temp_time_total_SQL = """SELECT temp, hour_of_day, SUM(count) AS count, AVG(avg_severity) AS avg_severity 
                        FROM count_sev_by_temp_time
                        GROUP BY temp, hour_of_day
                        ORDER BY
                            CASE temp
                                WHEN 'below 0' THEN 0
                                WHEN '[0, 30)' THEN 1
                                WHEN '[30, 50)' THEN 2
                                WHEN '[50, 70)' THEN 3
                                WHEN '[70, 90)' THEN 4
                                WHEN 'over 90' THEN 5
                            END;"""
temp_time_total_df = executeSQL(temp_time_total_SQL)
temp_time_total_df['tooltip'] = "Count: " + temp_time_total_df['count'].astype(str) + "<br>" + temp_time_total_df['avg_severity'].apply(lambda x: f"Mean Severity: {x:.2f}")



temp_vis_SQL = "SELECT * FROM count_sev_by_temp_vis"
temp_vis_df = executeSQL(temp_vis_SQL)
temp_vis_df['tooltip'] = "Count: " + temp_vis_df['count'].astype(str) + "<br>" + temp_vis_df['avg_severity'].apply(lambda x: f"Mean Severity: {x:.2f}")

temp_vis_total_SQL = """SELECT temp, vis, SUM(count) AS count, AVG(avg_severity) AS avg_severity  
                        FROM count_sev_by_temp_vis
                        GROUP BY temp, vis
                        ORDER BY
                            CASE temp
                                WHEN 'below 0' THEN 0
                                WHEN '[0, 30)' THEN 1
                                WHEN '[30, 50)' THEN 2
                                WHEN '[50, 70)' THEN 3
                                WHEN '[70, 90)' THEN 4
                                WHEN 'over 90' THEN 5
                            END,
                            CASE vis
                                WHEN '[0,2)' THEN 0
                                WHEN '[2,5)' THEN 1
                                WHEN '[5,10)' THEN 2
                                WHEN 'over 10' THEN 3
                            END;"""
temp_vis_total_df = executeSQL(temp_vis_total_SQL)
temp_vis_total_df['tooltip'] = "Count: " + temp_vis_total_df['count'].astype(str) + "<br>" + temp_vis_total_df['avg_severity'].apply(lambda x: f"Mean Severity: {x:.2f}")


#%%

# show all the data in df
def create_general_figure(df=vis_time_total_df, x_column='hour_of_day', y_column='vis', xaxis_title='Time of day (hour)', yaxis_title='Visibility (mi)'):
    return {
        'data': [
            dict(
                x=df[x_column],
                y=df[y_column],
                text=df['tooltip'],
                mode='markers',
                marker={
                    'size': np.log(df['count']) * 5,
                    'color': df['avg_severity'],
                    'colorscale': "Y10rRd",
                    'colorbar': dict(title = 'Mean Severity'),
                    'line': {'width': 0.5, 'color': 'white'}
                },
            ) 
        ],
        'layout': dict(
            xaxis={'title': xaxis_title, 'tickvals': df[x_column]},
            yaxis={'title': yaxis_title},
            legend={'x': 0, 'y': 1},
            margin={'l': 100, 'b': 100, 't': 50, 'r': 80},
            hovermode='closest',
            font=dict(size=15),
            # transition = {'duration': 500}
        )          
    }

# used for bubble size legend, this is default
size_range = list(range(100, 50000, 10000))
bubble_size_fig = {
    'data': [
        dict(
            x=[1]*10,
            y=size_range,
            #text=vis_time_df['avg_severity'],
            mode='markers',
            opacity=0.8,
            marker={
                'size': np.log(size_range) * 5,
                'color': 'red',
                'line': {'width': 0.5, 'color': 'white'}

            },
            # showlegend=False
        ) 
    ]
    ,
    'layout': dict(
        xaxis=dict(zeroline=False, showgrid=False, showline=False,autorange=True, showticklabels=False ),
        yaxis=dict(zeroline=False, showgrid=False, showline=False, autorange=True, showticklabels=True),
        width=50
        # margin={'l': 100, 'b': 50, 't': 50, 'r': 80},
        # legend={'x': 0, 'y': 1},
        # hovermode='closest',
        # transition = {'duration': 500}
    )
}

bubblechart_names = ['Visibility vs. Time-of-day','Temperature vs. Time-of-day','Temperature vs. Visibility']
select_years = ['2016-2019 total','2016','2017','2018','2019']

layout_bubblechart = html.Div([
    html.H5(children = "Sum of accident numbers (bubble size) & Average of severity (bubble color) in", style={'text-align': 'center'}),
    html.H5(children = "", id="bubble_header1", style={'text-align': 'center'}),
    html.H6(children = "",id="bubble_header2", style={'text-align': 'center'}),

    html.Div([
        html.Label("Y vs. X", className='label'),
        html.Div([
            dcc.Dropdown(
                id='bubblechart_name',
                options=[{'label': i, 'value': i} for i in bubblechart_names],
                value='Visibility vs. Time-of-day'
            )
        ],
        style={'width': '75%', 'display': 'inline-block', 'verticalAlign':'middle'}),       
    ],
    style={'width':'25%', 'display': 'inline-block', 'verticalAlign':'middle'}),

    html.Div([
        html.Label("Select year", className='label'),
        html.Div([
            dcc.Dropdown(
                id='bubblechart_select_year',
                options=[{'label': i, 'value': i} for i in select_years],
                value='2016-2019 total'
            )
        ],
        style={'width':'20%', 'display': 'inline-block', 'verticalAlign':'middle'}),
    ],
    style={'width':'75%', 'display': 'inline-block', 'verticalAlign':'middle'}),

    html.Div([
    dcc.Graph(
        id='bubble_figure',
        figure=create_general_figure(),
        style={"height": "70vh"}
    )],
    # style={'width': '80%'}
    ),

    # html.Div([
    # dcc.Graph(
    #     id='bubble_size',
    #     figure = bubble_size_fig
    # )],
    #     style={'width': '20%'}
    # )

])



# show filtered data by given_year
def create_year_figure(given_year, df, x_column, y_column, xaxis_title, yaxis_title):
    filtered_df = df[df.year == given_year]
    return create_general_figure(filtered_df, x_column, y_column, xaxis_title, yaxis_title)

bubblechart_dict = {
    'Visibility vs. Time-of-day':{'df_total': vis_time_total_df, 'df':vis_time_df, 'x_column':'hour_of_day', 'y_column':'vis', 'xaxis_title':'Time of day (hour)', 'yaxis_title':'Visibility (mi)'},
    'Temperature vs. Time-of-day':{'df_total': temp_time_total_df, 'df':temp_time_df, 'x_column':'hour_of_day', 'y_column':'temp', 'xaxis_title':'Time of day (hour)', 'yaxis_title':'Temperature (F)'},
    'Temperature vs. Visibility':{'df_total': temp_vis_total_df, 'df':temp_vis_df, 'x_column':'vis', 'y_column':'temp', 'xaxis_title':'Visibility (mi)', 'yaxis_title':'Temperature (F)'}
}

@app.callback(
    [Output('bubble_figure', 'figure'),
    Output('bubble_header1','children'),
    Output('bubble_header2','children')],
    [Input('bubblechart_name','value'),
    Input('bubblechart_select_year','value')]
)
def update_figure(selected_bubblechart, selected_year):
    
    x_column = bubblechart_dict[selected_bubblechart]['x_column']
    y_column = bubblechart_dict[selected_bubblechart]['y_column']
    xaxis_title = bubblechart_dict[selected_bubblechart]['xaxis_title']
    yaxis_title = bubblechart_dict[selected_bubblechart]['yaxis_title']


    header1 = "{}".format(selected_bubblechart)
    header2 = "year: {}".format(selected_year)

    if selected_year == '2016-2019 total':
        df = bubblechart_dict[selected_bubblechart]['df_total']
        return create_general_figure(df,x_column,y_column,xaxis_title,yaxis_title), header1, header2
    else:
        df = bubblechart_dict[selected_bubblechart]['df']
        filtered_df = df[df.year == selected_year]
        return create_general_figure(filtered_df,x_column,y_column,xaxis_title,yaxis_title), header1, header2


# @app.callback(
#     Output('bubble_size', 'figure'),
#     [Input('bubblechart_name','value'),Input('bubblechart_select_year','value')]
# )
# def update_bubble_size(selected_bubblechart, selected_year):
#     df = bubblechart_dict[selected_bubblechart]['dataframe']
#     max_count = df.count.max()
#     min_count = df.count.min()
#     n = 5
#     size_range =list(range(min_count, max_count, (max_count-min_count)//n))

#     return {
#         'data': [
#         dict(
#             x=[1] * n,
#             y=size_range,
#             #text=vis_time_df['avg_severity'],
#             mode='markers',
#             opacity=0.8,
#             marker={
#                 'size': np.log(size_range) * 5,
#                 'color': 'red',
#                 'line': {'width': 0.5, 'color': 'white'}

#             },
#             # showlegend=False
#         ) 
#     ]
#     ,
#     'layout': dict(
#         xaxis={'title': 'Time of day'},
#         yaxis={'title': 'Visibility'},
#         margin={'l': 100, 'b': 50, 't': 50, 'r': 80},
#         legend={'x': 0, 'y': 1},
#         hovermode='closest',
#         transition = {'duration': 500}
#     )
# }

