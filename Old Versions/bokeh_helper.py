import geopandas as gpd
from geopandas import GeoDataFrame

import numpy as np
import pandas as pd

from bokeh.models import ColumnDataSource

def getLonLat(geom, coord_type):
    """Returns either longitudes and latitudes from geometry coordinate sequence. 
    Used with Polygon."""
    if coord_type == 'lon':
        return list(geom.coords.xy[0])
    elif coord_type == 'lat':
        return list(geom.coords.xy[1])

def getPolyCoords(geom, coord_type):
    """Returns the coordinates (longitudes or latitudes of edges of a Polygon exterior)"""
    ext = geom.exterior
    return getLonLat(ext, coord_type)

def multiPolygonHandler(multi_poly, coord_type):
    """Function for handling MultiPolygon. 
    Returns a list of coordinates where all parts of Multi-geometries are merged into a ginels list.
    Individual geomstries are separated with np.nan which is how Bokeh wants them. 
    # Bokeh documentation regarding the Multi-geometry issues can be found here 
    (it is an open issue) 
    # https://github.com/bokeh/bokeh/issues/2321"""
    for i, part in enumerate(multi_poly):
        if i == 0:
            coord_arrays = [] + getPolyCoords(part, coord_type) + ['NaN']
        else: 
            coord_arrays = coord_arrays + getPolyCoords(part, coord_type) + ['NaN']
    # Return the coordinates
    return coord_arrays

def getCoords(row, geom_col, coord_type):
    """
    Returns longitudes and latitude of a Polygon as a list. 
    Can handle also MultiPolygon."""
    # Get geometry
    geom = row[geom_col]
    
    if geom.geom_type == 'Polygon': 
        return list(getPolyCoords(geom, coord_type))
    else: 
        return list(multiPolygonHandler(geom, coord_type))

# set up data
def setColumnDataSource(df, col_list): 
    df['lon'] = df.apply(getCoords, geom_col = 'geometry', coord_type = 'lon', axis = 1)
    df['lat'] = df.apply(getCoords, geom_col = 'geometry', coord_type = 'lat', axis = 1)
        
    g_df = df[col_list].copy()
    g_source = ColumnDataSource(g_df)
    return g_source
