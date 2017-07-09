import pickle

from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler

import geopandas as gpd
from geopandas import GeoDataFrame

import numpy as np
import pandas as pd

from cluster_block_groups import cluster_block_groups

data_path = 'Data/'

with open('{}bk_gp_df_for_graph'.format(data_path), 'rb') as file_obj: 
    bk_gp_df_for_graph = pickle.load(file_obj)

# get the feature_list and val_list from user input
# picked_vals_results = request.form
# feature_list = [k for k, v in picked_vals_results.items()]
# val_list = [v for k, v in picked_vals_results.items()]

feature_list = ['med_hhld_inc', 'good trees']
val_list = [15000, 50]

cluster5, cluster_centers, cluster_val = \
    cluster_block_groups(bk_gp_df_for_graph, 5, feature_list, val_list)
print(cluster_centers)