import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from database import executeSQL
import numpy as np
from app import app
from util import state_abbr
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import dash
import pickle
import pandas as pd

month_num = {
    'January':'1',
    'February':'2',
    'March':'3',
    'April':'4',
    'May':'5',
    'June':'6',
    'July':'7',
    'August':'8',
    'September':'9',
    'October':'10',
    'November':'11',
    'December':'12',
}

week_num = {
    'Sunday':'0',
    'Monday':'1',
    'Tuesday':'2',
    'Wednesday':'3',
    'Thursday':'4',
    'Friday':'5',
    'Saturday':'6',
}

#=============================================================================================
# Rate Chart Components
# ===============

accident_rate_SQL = """
    SELECT * FROM accident_rate
"""
accident_rate_df = executeSQL(accident_rate_SQL)

default_color = 'lightslategray'
bar_colors = {k:default_color for k in accident_rate_df['state']}


def generate_ratechart(df=accident_rate_df, x_column='state', xaxis_title='State', given_color = bar_colors):
    return {
        'data': [
            dict(
                x=df[x_column],
                y=df['accident_percentage'],
                type='bar',
                marker={
                    'color':list(given_color.values()),
                },
            ) 
        ],
        'layout': dict(
            xaxis={'title': xaxis_title,'tickvals': df[x_column]},
            yaxis={'title': 'Accident Rate in Percentage (%)'},
            margin={'l': 100, 'b': 100, 't': 50, 'r': 80},
            hovermode='closest',
            font=dict(size=15),
        )
    }

layout_ratechart = html.Div([
    html.H6("State Accident Rate (%)", style={'text-align': 'center'}),
    dcc.Graph(
        id='rate_figure',
        figure=generate_ratechart(),
        style={"height": "80vh"}
    )
])

#=============================================================================================
# ML model components
# ===============
state_list = state_abbr.keys()
time_list = ['00:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00', '07:00', '08:00', '09:00', \
    '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', \
    '21:00', '22:00', '23:00', ]
week_list = week_num.keys()
month_list = month_num.keys()
weather_list = ('Cloudy','Clear','Rain','Haze','Snow','Fog')  # make sure it's a tuple otherwise mlmodelbackend will error
temperature_list = ['<0', '[0, 30)', '[30, 50)', '[50, 70)', '[70, 90)', '>=90']
visibility_list = ['Poor [0,2)', 'Moderate [2,5)', 'Good [5,10)', 'Very Good >=10']



layout_mlmodel = html.Div([

    html.H1("", id="mlm_blankline1"),

    html.Label([
        "Select state",
        dcc.Dropdown(
            id = 'model_state',
            options=[{'label': i, 'value': i} for i in state_list],
        ),
    ], className = 'ml_input'),

    html.Label([
        "Select time of day (hour)",
        dcc.Dropdown(
            id = 'model_time',
            options=[{'label': i, 'value': i} for i in time_list],
        ),
    ], className = 'ml_input'),

    html.Label([
        "Select day of the week",
        dcc.Dropdown(
            id = 'model_week',
            options=[{'label': i, 'value': i} for i in week_list],
        ),
    ], className = 'ml_input'),

    html.Label([
        "Select month",
        dcc.Dropdown(
            id = 'model_month',
            options=[{'label': i, 'value': i} for i in month_list],
        ),
    ], className = 'ml_input'),

    html.Label([
        "Select weather",
        dcc.Dropdown(
            id = 'model_weather',
            options=[{'label': i, 'value': i} for i in weather_list],
        ),
    ], className = 'ml_input'),


    html.Label([
        "Select temperature range (F)",
        dcc.Dropdown(
            id = 'model_temperature',
            options=[{'label': i, 'value': i} for i in temperature_list],
        ),
    ], className = 'ml_input'),

    html.Label([
        "Select visibility range (mi)",
        dcc.Dropdown(
            id = 'model_visibility',
            options=[{'label': i, 'value': i} for i in visibility_list],
        ),
    ], className = 'ml_input'),

    html.Label([
        dbc.Button("Apply", id="ml_apply", color="success"),
    ], className = 'ml_input'),

    

    html.Label([
        "Predicted accident severity is:",
        html.Div("",id="ml_output_placeholder")
    ], className = 'ml_output'),


])

#=============================================================================================
# Callbacks
# ===============
@app.callback(
    Output('rate_figure','figure'),
    [Input('model_state','value')]
)
def update_rate_figure(selected_state):
    if selected_state is not None:
        selected_state_abbr = state_abbr[selected_state]
        bar_colors = {k:default_color for k in accident_rate_df['state']}
        bar_colors[selected_state_abbr] = '#EF553B'
        return generate_ratechart(given_color = bar_colors)
    else:
        return generate_ratechart()

@app.callback(
    Output('ml_output_placeholder','children'),
    [Input('model_state','value'), Input('model_time','value'), Input('model_week','value'), Input('model_month','value'), \
        Input('model_weather','value'), Input('model_temperature','value'), Input('model_visibility','value'), Input('ml_apply','n_clicks')]
)
def model_predict(state, time, week, month, weather, temperature, visibility, btn_apply):
    if state is None or time is None or week is None or month is None or weather is None or temperature is None or visibility is None or btn_apply is None:
        raise PreventUpdate
    else:
        # apply button
        ctx = dash.callback_context
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]  

        if button_id == "ml_apply":
            with open("rf_model.pkl", 'rb') as file:
                # create dataframe with all zeros in the features
                model = pickle.load(file)
                col_names = model.feature_names
                temp_np = np.zeros(shape=(1,len(col_names)))
                df = pd.DataFrame(temp_np, columns=col_names)

                # apply correct value to each columns
                hour_of_day = int(time[0:2])
                df.at[0, 'hour_of_day'] = hour_of_day

                f1 = 'state_'+state_abbr[state]
                df.at[0, f1] = 1

                f2 = 'temperature_'+temperature
                df.at[0, f2] = 1

                f3 = 'month_'+month_num[month]
                df.at[0, f3] = 1

                f4 = 'day_of_wk_'+week_num[week]
                df.at[0, f4] = 1

                f5 = 'visibility_'+visibility
                df.at[0, f5] = 1

                f6 = 'weather_'+weather
                df.at[0, f6] = 1

                predicted_sev = model.predict(df)
                return predicted_sev


        

