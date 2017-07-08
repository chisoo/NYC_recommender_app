import pickle

from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler

import geopandas as gpd
from geopandas import GeoDataFrame

import numpy as np
import pandas as pd

from bokeh.io import show
from bokeh.plotting import figure, save
from bokeh.models import ColumnDataSource, HoverTool, LogColorMapper

from bokeh_helper import setColumnDataSource

data_path = 'Data/'

with open('{}nynta_shape_df'.format(data_path), 'rb') as file_obj: 
    boundary_df = pickle.load(file_obj)

with open('{}cluster5'.format(data_path), 'rb') as file_obj: 
    cluster5 = pickle.load(file_obj)

cluster_df = cluster5[cluster5['cluster'] == 1].copy()

cluster_source = setColumnDataSource(cluster_df, ['lon', 'lat'])
nynta_source = setColumnDataSource(boundary_df, ['lon', 'lat', 'NTAName'])

# initialize the figure
p = figure()

# plot the cluster and boundary
p.patches('lon', 'lat', fill_color = 'blue', alpha = 0.5, source = cluster_source)
p.patches('lon', 'lat', fill_color = None, line_color = 'black', 
            source = nynta_source, line_width = 1)

# save the figure
output_file = r"templates/cluster_graph_test.html"
save(p, output_file)