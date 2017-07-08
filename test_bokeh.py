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

with open('{}cluter5'.format(data_path), 'rb') as file_obj: 
    cluster5 = pickle.load(file_obj)

geo_df_val = cluster5[cluster5['cluster'] == int(cluster_val)].copy()

color_dict = {0: 'blue', 1: 'green', 2: 'yellow', 3: 'red', 4: 'pink'}
cluster5_val['color'] = cluster5_val['cluster'].apply(lambda x: color_dict[x])

cluster_source = setColumnDataSource(cluster5_val, ['lon', 'lat', 'color'])
nynta_source = setColumnDataSource(boundary_df, ['lon', 'lat'])

# initialize the figure
p = figure()

# plot the cluster and boundary
p.patches('lon', 'lat', fill_color = 'color', alpha = 0.5, source = cluster_source)
p.patches('lon', 'lat', fill_color = None, line_color = 'black', 
            source = nynta_source, line_width = 1)

show(p)

# save the figure
output_file = r"{}/cluster_graph.html"
save(p, output_file)