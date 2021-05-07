# -*- coding: utf-8 -*-
"""
Created on Fri Mar  6 21:02:59 2020

@author: zhaol
"""
import sqlite3
import pandas as pd
import sys

def executeSQL(query):
    conn = None
    try:
        conn = sqlite3.connect("accidents.db")
    except:
        print(sys.exc_info()[0],"occured")
    df = pd.read_sql_query(query,conn)
    return df

# Example of how to write SQL method! You don't need to use it!
def locationsOnMap():
    listLocations = """
        SELECT Start_Lat, Start_Lng
        FROM accidents
        WHERE State='CA';
    """
    return executeSQL(listLocations)

def loadPointsInBBox(bbox) -> pd.DataFrame:
    '''Load points within the bounding box

    Args:
        bbox: (tuple/list) upperleft and bottomright corner coordinates of the bounding box.
    Returns:
        df: (pd.DataFrame) query results
    '''
    upperleft, bottomright = bbox[:2]
    