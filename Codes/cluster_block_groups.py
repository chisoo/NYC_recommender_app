# setup
import numpy as np
import pandas as pd
import pickle

import geopandas as gpd
from geopandas import GeoDataFrame

from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler

# set the paths for data and graphs
data_path = "../../Data/"

def cluster_block_groups(num_clusters, feature_list):
    """
    Parameters
    ----------
    num_clusters (int)
    feature_list (list): list of variables to use in the clustering
    """
    # read in data
    with open('{}pickled_data/bk_gp_df_for_graph'.format(data_path), 'rb') as file_obj:
        bk_gp_df = pickle.load(file_obj)
        
    ### prepare data for clustering
    bk_gp_df.set_index('GEOID', inplace = True)
    bk_gp_df.head(3)

    # pick only relevant variables
    bk_gp_df_for_ml = bk_gp_df[feature_list].copy()

    # fill in NA
    bk_gp_df_for_ml = bk_gp_df_for_ml.fillna(0)

    # scale
    scaler = MinMaxScaler()

    # fit the data
    scaler.fit(bk_gp_df_for_ml)

    # scale the data
    bk_gp_df_for_ml_scaled = scaler.transform(bk_gp_df_for_ml)

    ### Clustering
    kmeans = KMeans(n_clusters = num_clusters, random_state = 0)
    clusters = kmeans.fit(bk_gp_df_for_ml_scaled)
    bk_gp_df_for_ml['cluster'] = pd.Series(clusters.labels_, index = bk_gp_df_for_ml.index)

    # check the 'distribution' of clusters
    bk_gp_df_clustered = bk_gp_df_for_ml.copy()
    bk_gp_df_clustered['cluster'].value_counts()

    # prepare the data with GEOID
    bk_gp_df_clustered.reset_index(inplace = True)
    bk_gp_df.reset_index(inplace = True)

    bk_gp_df_clustered_w_geo = bk_gp_df_clustered[['GEOID', 'cluster']].merge(bk_gp_df)

    # make dataframe as geodataframe
    bk_gp_df_clustered_w_geo = GeoDataFrame(bk_gp_df_clustered_w_geo, geometry = bk_gp_df_clustered_w_geo['geometry'])

    # pickle the data
    return bk_gp_df_clustered_w_geo