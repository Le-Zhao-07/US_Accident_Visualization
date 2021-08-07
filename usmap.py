# -*- coding: utf-8 -*-
"""
Created on Fri Mar  6 22:23:17 2020
@author: Le Zhao, Yangzhan Yang, Zhiqi Yu
"""
import dash
import dash_core_components as dcc
import dash_html_components as html
from app import app
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import numpy as np

from opencage.geocoder import OpenCageGeocode
from opencage.geocoder import InvalidInputError, RateLimitExceededError, UnknownError

import copy
import json
import time
from collections import OrderedDict
from database import executeSQL
from util import state_abbr


#=============================================================================================
# Search Dangerous Road Components
# ===============
address_group = dbc.InputGroup(
    [
        dbc.InputGroupAddon("Address", addon_type="prepend"),
        dbc.Input(id="input_address", placeholder="Zipcode", type="text")
    ],
    size = 'lg',
)

warning_dialog = dcc.ConfirmDialog(
    id='dlg_warning',
    message='No results! Please formalize your address!'
)

no_result_dialog = dcc.ConfirmDialog(
    id="dlg_noresult",
    message="No dangerous road found."
)

search_button = dbc.Button("Search", id="btn_search", color="success", className="mr-1")

list_group = dbc.ListGroup(
    [
        dbc.ListGroupItem("", id="rank1"),
        dbc.ListGroupItem("", id="rank2"),
        dbc.ListGroupItem("", id="rank3"),
        dbc.ListGroupItem("", id="rank4"),
        dbc.ListGroupItem("", id="rank5")
    ],
    id="rank_list"
)

# Search layout element
layout_search = html.Div([
    dbc.Row([
        dbc.Col([html.H5("Search dangerous roads nearby")],width=12)
    ]),
    dbc.Row([
        dbc.Col([html.H6("Score: sum of accident severity on a road")])
    ]),
    dbc.Row([
        dbc.Col([address_group],width=9),
        dbc.Col([search_button], width=3) 
    ]),
    dbc.Row([
        dbc.Col([list_group], width=12)
    ]),
    warning_dialog,
    no_result_dialog,
],
style={"padding-left":"0.5rem", "padding-top":"1rem"})



#=============================================================================================
# Map Filter Components
# ===============

filterResult_temp = {"year":"", "severity":"", "weather":"", "visibility":""}
filterResult = {"year":"", "severity":"", "weather":"", "visibility":""}

layout_mapfilter = html.Div([
    
    dbc.Card(
        [dbc.CardBody(
                [
                    html.H6("Select year:", id="year", className="title"),
                    dbc.Button("2016", id="Year2016", color="info", className="mr-1"),
                    dbc.Button("2017", id="Year2017", color="info", className="mr-1"),
                    dbc.Button("2018", id="Year2018", color="info", className="mr-1"),
                    dbc.Button("2019", id="Year2019", color="info", className="mr-1"),
                ],
            style={"padding-top":"1px", 'float':'top','postion':'relative'},
            ),
        ],
        style={"padding-right":"0.5", "height":"3.5", "padding-top":"1px",'float':'top','postion':'relative'},
    ),    
    html.H6("", id="blankline1"),
    dbc.Card(
        [dbc.CardBody(
                [
                    html.H6("Select severity:", id="severity", className="title"),
                    dbc.Button("1", id="sev1", color="info", className="mr-1"),
                    dbc.Button("2", id="sev2", color="info", className="mr-1"),
                    dbc.Button("3", id="sev3", color="info", className="mr-1"),
                    dbc.Button("4", id="sev4", color="info", className="mr-1"),
                ],
            style={"padding-top":"1px", 'float':'top','postion':'relative'},
            ),
        ],
        style={"width": "47", "height":"3.5", "padding-top":"1px",'float':'top','postion':'relative'},
    ),    
    html.H6("", id="blankline2"),
    dbc.Card(
        [dbc.CardBody(
                [
                    html.H6("Select weather:", id="weather", className="title"),
                    dbc.Button("Clear", id="weather_Clear", color="info", className="mr-1"),
                    dbc.Button("Cloudy", id="weather_Cloudy", color="info", className="mr-1"),
                    dbc.Button("Rain", id="weather_Rain", color="info", className="mr-1"),
                    dbc.Button("Snow", id="weather_Snow", color="info", className="mr-1"),
                    dbc.Button("Windy", id="weather_Windy", color="info", className="mr-1"),
                    dbc.Button("Fog", id="weather_Fog", color="info", className="mr-1"),
                ],
            style={"padding-top":"1px",'float':'top','postion':'relative'},
            ),
        ],
        style={"width": "47", "height":"3.5", "padding-top":"1px",'float':'top','postion':'relative'},
    ),    
    
    html.H6("", id="blankline3"),
    dbc.Card(
        [dbc.CardBody(
                [
                    html.H6("Select visibility:", id="visibility", className="title"),
                    dbc.Button("0-2", id="v0-2", color="info", className="mr-1"),
                    dbc.Button("2-5", id="v2-5", color="info", className="mr-1"),
                    dbc.Button("5-10", id="v5-10", color="info", className="mr-1"),
                    dbc.Button(">10", id="v>10", color="info", className="mr-1"),
                ],
            style={"padding-top":"1px",'float':'top','postion':'relative'},
            ),
        ],
        style={"width": "47", "height":"4.5", "padding-top":"1px",'float':'top','postion':'relative'},
    ),
    html.H6("", id="blankline4"),
    dbc.Row([
        dbc.Col(dbc.ButtonGroup([
            dbc.Button("Apply", id="applyFilter", color="success", className="mr-1"),
            dbc.Button("Reset", id="resetFilter", color="secondary", className="mr-1")
        ]), width=4),
    ]),

],
    style={"padding-left":"0.2rem", "padding-top":"0.5rem", "padding-bottom":"0.5rem"}
)


@app.callback(
    Output("year", "children"), [Input("Year2016", "n_clicks"),Input("Year2017", "n_clicks"),Input("Year2018", "n_clicks"),Input("Year2019", "n_clicks"),Input("resetFilter", "n_clicks"),],
)
def on_button_click(n1, n2, n3, n4, n5):
    if n1 is None and n2 is None and n3 is None and n4 is None:
        return "Select year:"
    else:
        ctx = dash.callback_context
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if button_id == "resetFilter":
            filterResult_temp["year"] = ""
            filterResult["year"] = ""
            return "Select year:"
        else:
            filterResult_temp["year"] = button_id[4:]
            print(filterResult_temp["year"])    
            result_str = "Select year: " + filterResult_temp["year"]
            return result_str
        
@app.callback(
    Output("severity", "children"), [Input("sev1", "n_clicks"),Input("sev2", "n_clicks"),Input("sev3", "n_clicks"),Input("sev4", "n_clicks"),Input("resetFilter", "n_clicks"),],
)
def on_button_click(n1, n2, n3, n4, n5):
    if n1 is None and n2 is None and n3 is None and n4 is None:
        return "Select severity: "
    else:
        ctx = dash.callback_context
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if button_id == "resetFilter":
            filterResult_temp["severity"] = ""
            filterResult["severity"] = ""
            return "Select severity:"
        else:
            filterResult_temp["severity"] = button_id[3:]
            result_str = "Select severity: " + filterResult_temp["severity"]
            return result_str

@app.callback(
    Output("weather", "children"), [Input("weather_Clear", "n_clicks"),Input("weather_Cloudy", "n_clicks"),Input("weather_Rain", "n_clicks"),Input("weather_Snow", "n_clicks"),Input("weather_Windy", "n_clicks"),Input("weather_Fog", "n_clicks"),Input("resetFilter", "n_clicks"),],
)
def on_button_click(n1, n2, n3, n4, n5, n6, n7):
    if n1 is None and n2 is None and n3 is None and n4 is None and n5 is None and n6 is None:
        raise PreventUpdate
    else:
        ctx = dash.callback_context
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if button_id == "resetFilter":
            filterResult_temp["weather"] = ""
            filterResult["weather"] = ""
            return "Select weather:"
        else:
            filterResult_temp["weather"] = button_id[8:]
            print(filterResult_temp["weather"])    
            result_str = "Select weather: " + filterResult_temp["weather"]
            return result_str

@app.callback(
    Output("visibility", "children"), [Input("v0-2", "n_clicks"),Input("v2-5", "n_clicks"),Input("v5-10", "n_clicks"),Input("v>10", "n_clicks"),Input("resetFilter", "n_clicks"),],
)
def on_button_click(n1, n2, n3, n4, n5):
    if n1 is None and n2 is None and n3 is None and n4 is None and n5 is None:
        return "Select visibility: "
    else:
        ctx = dash.callback_context
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if button_id == "resetFilter":
            filterResult_temp["visibility"] = ""
            filterResult["visibility"] = ""
            return "Select visibility:"
        else:
            filterResult_temp["visibility"] = button_id[1:]  
            result_str = "Select visibility: " + filterResult_temp["visibility"]
            return result_str

#=============================================================================================
# Map Components
# ===============

map_margin = {"r":0,"t":0,"l":0,"b":0}

where_clause_dict = {
    "year": "strftime('%Y', Start_Time)=",
    "severity": "Severity=",
    "weather": "lower(Weather_Condition)=",
    "visibility": '"Visibility(mi)"'
}

subtable_sql = ""

def load_choropleth(filter_result=None):
    """Load choropleth map
    Args:
        filter_result (dict): filters that should be applied to data. Default to None, 
            means no filters applied.
    
    Returns:
        choropleth_state_data (dict): state-level choropleth map object to be used in plot.ly Figure object.
        choropleth_county_data (dict): county-level choropleth map object to be used in plot.ly Figure object. 
    """
    if filter_result is None:
        filter_result = {}

    where_clauses = []

    for key in filter_result:
        if key == "weather":
            where_clauses.append(where_clause_dict[key] + '"' + str.lower(filter_result[key]) + '"')
        elif key == "visibility":
            range_str = filter_result[key]
            if '-' in range_str:
                lower, upper = range_str.split('-')
                where_clauses.append(where_clause_dict[key] + ">" + '"' + lower + '"' + " and " + where_clause_dict[key] + "<=" + '"'+ upper + '"')
            else:
                # the right-most range, e.g. >10
                where_clauses.append(where_clause_dict[key] + ">" + '"' + filter_result[key][1:] + '"')
        else:
            where_clauses.append(where_clause_dict[key] + '"' + filter_result[key] + '"')

    where_clause = " and ".join(where_clauses)

    global subtable_sql

    # SQL 
    if where_clause == "":
        state_sql = """
            select State as state_abbr, count(*) as ta_count 
            from accidents
            group by State;
        """

        county_sql = """
            select County, State, count(*) as county_count
            from accidents
            group by County, State;
        """
    else:
        subtable_sql = """
            select State, County, Severity, "Visibility(mi)", lower(Weather_Condition), strftime('%Y', Start_Time), Start_Lng, Start_Lat, Street
            from accidents
            where {}
        """.format(where_clause)

        state_sql = """
            select State as state_abbr, count(*) as ta_count
            from ({}) as t1
            group by State;
        """.format(subtable_sql)

        county_sql = """
            select County, State, count(*) as county_count
            from ({}) as t1
            group by County, State;
        """.format(subtable_sql)

    state_count = executeSQL(state_sql)
    county_count = executeSQL(county_sql)
    county_count.loc[:, "county_id"] = county_count.loc[:, "State"] + "-" + \
                                    county_count.loc[:, "County"]

    # 2. choropleth map data object
    global choropleth_state_data 
    
    choropleth_state_data = {
        'type': 'choroplethmapbox',
        'geojson': states,
        'featureidkey': "properties.state_abbr",
        'locations': state_count.state_abbr,
        'z': np.log10(state_count.ta_count),
        'colorscale': "Y10rRd",      
        'showlegend': True,
        'name': "State",
        'colorbar': {'len': 0.7,
                     'title': '#Accidents',
                     'tickvals': [1, 2, 3, 3.699, 4, 4.477, 4.778],
                     'ticktext': ['10', '100', '1k', '5k','10k','30k','60k'],
                     'opacity': 0.8,},
        'visible': True,
        'text': ['State: {}<br>Number of Accidents: {}'.format(state_count.state_abbr[i], state_count.ta_count[i]) for i in range(state_count.shape[0])],
        'hoverinfo': "text",
        'opacity': 0.8,
    }

    global choropleth_county_data

    choropleth_county_data = {
        'type': 'choroplethmapbox',
        'geojson': counties,
        'featureidkey': "properties.county_id",
        'locations': county_count.county_id,
        'z': np.log10(county_count.county_count),
        'colorscale': "Y10rRd",
        'showlegend': True,
        'name': "County",
        'colorbar': {'len': 0.7,
                     'title': '#Accidents',
                     'tickvals': [1, 2, 3, 3.699, 4, 4.477, 4.778],
                     'ticktext': ['10', '100', '1k', '5k','10k','30k','60k'],
                     'opacity': 0.8,},
        'visible': True,
        'text': ['County: {}<br>Number of Accidents: {}'.format(county_count.county_id[i], county_count.county_count[i]) for i in range(county_count.shape[0])],
        'hoverinfo': "text",
        'opacity': 0.8,
    }

    return choropleth_state_data, choropleth_county_data

def load_point_data(bbox):

    global subtable_sql
    ul, ur, lr, ll = bbox

    if subtable_sql == "":
        scatter_query = '''
            select * from accidents
            where Start_Lng > {} and Start_Lat < {} and 
                    Start_Lng < {} and Start_Lat > {};
        '''.format(ul[0], ul[1], lr[0], lr[1])
    else:
        scatter_query = '''
            select * 
            from ({}) as t
            where Start_Lng > {} and Start_Lat < {} and 
                    Start_Lng < {} and Start_Lat > {};
        '''.format(subtable_sql, ul[0], ul[1], lr[0], lr[1])

    point_df = executeSQL(scatter_query)

    return point_df

def create_point_data(point_df, zoomLevel): 
    point_data = {
        'type': 'scattermapbox',
        'lat': point_df['Start_Lat'],
        'lon': point_df['Start_Lng'],
        'marker': {
            'opacity': 0.8,
            'size': zoomLevel/1.5,
            'color': point_df['Severity'],
            'cmin': 1,
            'cmax': 4,
            'autocolorscale': True
        },
        # 'text': 'Severity: ' + point_df['Severity'].astype(str) + '<br>Time: ' + point_df['Start_Time'],
        'text': 'Severity: ' + point_df['Severity'].astype(str),
        # 'showscale': False,
        'name': "accidents"
    }

    return point_data


def create_map_fig(choropleth_state_data, choropleth_county_data, boundary_box, choropleth_layer='state', zoom=3.5, center=dict(lat= 37.0902, lon=-95.7129)):
    """Create Plot.ly Figure object 
    
    Create figure object using state-level and county-level choropleth map data object.
    Args:
        choropleth_state_data (dict): state-level choropleth map object to be used in plot.ly Figure object.
        choropleth_county_data (dict): county-level choropleth map object to be used in plot.ly Figure object.
        boundary_box (list): dictionary will be used to generate point data when zoom level > 8.
        choropleth_layer (string): decide to load either state or county choropleth layer when zoom level < 8
        zoom (number): map zoom level, default is 4. 
        center (dict): map center object {'lat': xx, 'lon': xx}, default is the center of the U.S.
    
    Returns:
        dict: the map figure to be plotted.
    """
    # mapbox stuff
    mapbox_access_token = "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNqdnBvNDMyaTAxYzkzeW5ubWdpZ2VjbmMifQ.TXcBE-xg9BFdV2ocecc_7g"
    base_map = "carto-positron" 

    # 3. default figure object: load state and county choropleth map
    # when zoom level < 8, only load state and county choropleth map, else only load point data
    if zoom < 8:
        if choropleth_layer == 'state':
            choropleth_state_data['visible']=True
            map_fig = dict(
                data=[choropleth_state_data],
                layout=dict(
                    mapbox=dict(
                        layers=[],
                        accesstoken=mapbox_access_token,
                        style=base_map,
                        center=center,
                        zoom=zoom,
                    ),
                    autosize=True,
                    margin=map_margin
                )
            )
        elif choropleth_layer == 'county':
            choropleth_state_data['visible']=True
            map_fig = dict(
                data=[choropleth_county_data],
                layout=dict(
                    mapbox=dict(
                        layers=[],
                        accesstoken=mapbox_access_token,
                        style=base_map,
                        center=center,
                        zoom=zoom,
                    ),
                    autosize=True,
                    margin=map_margin
                )
            )
        else:
            choropleth_state_data['visible']=False
            map_fig = dict(
                data=[choropleth_state_data],
                layout=dict(
                    mapbox=dict(
                        layers=[],
                        accesstoken=mapbox_access_token,
                        style=base_map,
                        center=center,
                        zoom=zoom,
                    ),
                    autosize=True,
                    margin=map_margin
                )
            )
        
    else:
        # -- Load scattered points -- 
        point_df = load_point_data(boundary_box)
        point_data = create_point_data(point_df,zoom)
        map_fig = dict(
            data=[point_data],
            layout=dict(
                mapbox=dict(
                    layers=[],
                    accesstoken=mapbox_access_token,
                    style=base_map,
                    center=center,
                    zoom=zoom,
                ),
                autosize=True,
                margin=map_margin
            )
        )        

    return map_fig


# ===============
# Initial load-up
# ===============

# 1. load up state and county boundary geojson files
with open("data/states.json") as state_file, open("data/counties.json") as county_file:
    states = json.load(state_file)
    counties = json.load(county_file)

# 2. create figure object
choropleth_state_data, choropleth_county_data = load_choropleth(None)
default_map_fig = create_map_fig(choropleth_state_data, choropleth_county_data, [])

# 3. map layout component to be exported
layout_map = html.Div([
    dcc.Graph(
        id='map',
        figure=default_map_fig,
        config={"displayModeBar": False},
        style={"height": "80vh"}
    ),
    dcc.Dropdown(
        id='dd_state_county',
        options=[
            {'label':'state', 'value':'state'},
            {'label':'county', 'value':'county'},
            {'label':'no choropleth', 'value':'no choropleth layer'},
        ],
        value='state',     
    )
], style={"padding-left":"0.2rem", "padding-top":"0.5rem", "padding-bottom":"0.5rem", "position":"relative"})


# ==========
# Callbacks
# ==========

# a tracker of the last event
isNewest = OrderedDict({})

@app.callback(
    [Output("map", "figure"), Output("rank1", "children"), Output("rank2", "children"), Output("rank3", "children"), \
        Output("rank4", "children"), Output("rank5", "children"), Output("dlg_warning", "displayed"), Output("dlg_noresult", "displayed")],
    [Input("applyFilter", "n_clicks"), Input("resetFilter", "n_clicks"), Input("btn_search", "n_clicks"), \
        Input("map", "relayoutData"), Input("dd_state_county", "value")],
    [State("input_address", "value")]
)
def on_remap(btn_apply, btn_reset, btn_search, relayoutData, layer_selector, input_address):

    global choropleth_state_data, choropleth_county_data, subtable_sql

    ctx = dash.callback_context
    event_id = ctx.triggered[0]["prop_id"].split(".")[0]

    # ===================
    # map zoom events
    # ===================
    if event_id == "map":
        # relayout event
        if relayoutData is None or 'autosize' in relayoutData:
            raise PreventUpdate

        else:
            # -- Check if the current event is the newest after a short interval --
            global isNewest

            # check if there is an old event, if yes, then pop it out and record this new event
            if len(isNewest) != 0:
                isNewest.popitem(last=False)

            # use the current time of event as key to record the event
            cur_time = time.time()
            isNewest[cur_time] = 1

            # sleep for 0.5 second
            time.sleep(0.5)

            # recheck if no new event comes, if not, then prevent update
            if cur_time not in isNewest:
                raise PreventUpdate

            # copy the default map fig 
            map_fig = create_map_fig(choropleth_state_data, choropleth_county_data, relayoutData['mapbox._derived']['coordinates'],
                choropleth_layer=layer_selector, 
                center=dict(lat= relayoutData['mapbox.center']['lat'], lon=relayoutData['mapbox.center']['lon']), 
                zoom=relayoutData['mapbox.zoom']
            )

        return map_fig, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    # ===================
    # select state or county events
    # ===================
    elif event_id == "dd_state_county":

        if (relayoutData is None) or ('autosize' in relayoutData):
            map_fig = create_map_fig(choropleth_state_data, choropleth_county_data, [], choropleth_layer=layer_selector)
        else:
            if relayoutData['mapbox.zoom']<8:
                map_fig = create_map_fig(choropleth_state_data, choropleth_county_data, [], choropleth_layer=layer_selector, center=dict(
                        lat= relayoutData['mapbox.center']['lat'], lon=relayoutData['mapbox.center']['lon']
                        ), zoom=relayoutData['mapbox.zoom'])
            else:

                map_fig = create_map_fig(choropleth_state_data, choropleth_county_data, relayoutData['mapbox._derived']['coordinates'], choropleth_layer=layer_selector, center=dict(
                        lat= relayoutData['mapbox.center']['lat'], lon=relayoutData['mapbox.center']['lon']
                        ), zoom=relayoutData['mapbox.zoom'])
        return map_fig, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    # ===================
    # button click events
    # ===================
    elif event_id == "applyFilter":
        filterResult = copy.deepcopy(filterResult_temp)

        # pop out empty filter entries
        for key in list(filterResult):
            if filterResult[key] == "":
                filterResult.pop(key)

        # reload map 
        choropleth_state_data, choropleth_county_data = load_choropleth(filterResult)

        if (relayoutData is None) or ('autosize' in relayoutData):
            map_fig = create_map_fig(choropleth_state_data, choropleth_county_data, [], choropleth_layer=layer_selector)
        else:
            if relayoutData['mapbox.zoom']<8:
                map_fig = create_map_fig(choropleth_state_data, choropleth_county_data, [], choropleth_layer=layer_selector, center=dict(
                        lat= relayoutData['mapbox.center']['lat'], lon=relayoutData['mapbox.center']['lon']
                        ), zoom=relayoutData['mapbox.zoom'])
            else:

                map_fig = create_map_fig(choropleth_state_data, choropleth_county_data, relayoutData['mapbox._derived']['coordinates'], choropleth_layer=layer_selector, center=dict(
                        lat= relayoutData['mapbox.center']['lat'], lon=relayoutData['mapbox.center']['lon']
                        ), zoom=relayoutData['mapbox.zoom'])

        return map_fig, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    elif event_id == "resetFilter":
        subtable_sql = ""
        choropleth_state_data, choropleth_county_data = load_choropleth(None)

        if (relayoutData is None) or ('autosize' in relayoutData):
            map_fig = create_map_fig(choropleth_state_data, choropleth_county_data, [], choropleth_layer=layer_selector)
        else:
            if relayoutData['mapbox.zoom']<8:
                map_fig = create_map_fig(choropleth_state_data, choropleth_county_data, [], choropleth_layer=layer_selector, center=dict(
                        lat= relayoutData['mapbox.center']['lat'], lon=relayoutData['mapbox.center']['lon']
                        ), zoom=relayoutData['mapbox.zoom'])
            else:

                map_fig = create_map_fig(choropleth_state_data, choropleth_county_data, relayoutData['mapbox._derived']['coordinates'], choropleth_layer=layer_selector, center=dict(
                        lat= relayoutData['mapbox.center']['lat'], lon=relayoutData['mapbox.center']['lon']
                        ), zoom=relayoutData['mapbox.zoom'])
        return map_fig, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    elif event_id == "btn_search":
        if input_address is None or input_address == "":
            raise PreventUpdate
        else:
            coordinates = geocode_address(input_address)

            if coordinates is None:
                # something wrong, either with OpenCage or with input address
                return dash.no_update, "", "", "", "", "", True, dash.no_update
            else:
                # generate the 30 mile bounding box around the center point
                subtable_sql = ""
                bbox = calculate_bounding_box(coordinates, 30)
                point_df = load_point_data(bbox)

                # copy the default map fig 
                map_fig = create_map_fig(choropleth_state_data, choropleth_county_data, bbox, choropleth_layer=layer_selector, center=dict(
                    lat=coordinates['lat'], lon=coordinates['lng']
                ), zoom=9)


                # -- Update the rank result --
                rank_result = rank_roads(point_df)

                # format output text
                num_record = rank_result.shape[0]
                return_list = [map_fig]
                for i in range(min(num_record, 5)):
                    return_list.append(format_result(rank_result.iloc[i]))
                for j in range(5 - num_record):
                    return_list.append("")

                # add no_update to address warning dialog
                return_list.append(dash.no_update)
                
                # last output: check if there is no result after thresholding
                if len(rank_result) == 0:
                    return_list.append(True)
                else:
                    return_list.append(dash.no_update)
                    
                return return_list

def rank_roads(point_df):
    """Rank road dangerousness
    
    Args:
        point_df (pandas.DataFrame): dataframe 
    """
    point_df.loc[:, 'weights'] = point_df.loc[:, "Severity"]
    rank_result = point_df.groupby("Street").sum().reset_index()
    rank_result.sort_values("weights", ascending=False, inplace=True)

    # only return roads that have score higher than 
    return rank_result.loc[rank_result["weights"] > 417, :]

def format_result(record):
    return record["Street"] + " (score: " + str(record["weights"]) + ")"

def geocode_address(address):

    # example result:
    # [{'components': {'city': 'Bordeaux',
    #                  'country': 'France',
    #                  'country_code': 'fr',
    #                  'county': 'Bordeaux',
    #                  'house_number': '11',
    #                  'political_union': 'European Union',
    #                  'postcode': '33800',
    #                  'road': 'Rue Sauteyron',
    #                  'state': 'New Aquitaine',
    #                  'suburb': 'Bordeaux Sud'},
    #   'formatted': '11 Rue Sauteyron, 33800 Bordeaux, France',
    #   'geometry': {'lat': 44.8303087, 'lng': -0.5761911}}]

    opencage_api_key = "1383b9ee671d4d2ea7abfe273586679a"
    geocoder = OpenCageGeocode(opencage_api_key)

    coordinates = None

    try:
        results = geocoder.geocode(address, no_annotations=1, language='en')
        if results and len(results):
            i = 0
            while i < len(results) and results[i]['components']['country_code'] != 'us':
                i += 1
            coordinates = results[i]['geometry'] if i < len(results) else None
        else:
            # no results, return None
            return None

    except UnknownError:
        print("OpenCage Geocoder: unknown error.")
    except RateLimitExceededError as ex:
        print(ex)

    return coordinates

def calculate_bounding_box(center, offset):
    # offset mile to degree
    mile_per_lat = 69.172
    mile_per_lng = 69.172 * np.cos(np.pi/180 * center['lat'])

    offset_lat = offset / mile_per_lat
    offset_lng = offset / mile_per_lng

    center_lat = center['lat']
    center_lng = center['lng']
    ul = [center_lng - offset_lng, center_lat + offset_lat]
    ur = [center_lng + offset_lng, center_lat + offset_lat]
    lr = [center_lng + offset_lng, center_lat - offset_lat]
    ll = [center_lng - offset_lng, center_lat - offset_lat]
    bbox = [ul, ur, lr, ll]

    return bbox