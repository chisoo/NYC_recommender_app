# setup
import numpy as np
import pandas as pd
import pickle

import geopandas as gpd
from geopandas import GeoDataFrame

from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler

def cluster_block_groups(bk_gp_df, num_clusters, feature_list, val_list):
    """
    Parameters
    ----------
    bk_gp_df (DataFrame)
    num_clusters (int)
    feature_list (list): list of variables to use in the clustering
    val_list (list): list of values for each variables the user chose

    OUTPUT
    ----------
    bk_gp_df_clustered_w_geo, cluster_centers, cluster_val
    """
    ### prepare data for clustering
    bk_gp_df.set_index('GEOID', inplace = True)
    bk_gp_df.head(3)
    print(feature_list)
    # pick only relevant variables
    bk_gp_df_for_ml = bk_gp_df[feature_list].copy()

    # fill in NA
    bk_gp_df_for_ml = bk_gp_df_for_ml.fillna(0)

    # scale the data
    scaler = MinMaxScaler()
    scaler.fit(bk_gp_df_for_ml)
    bk_gp_df_for_ml_scaled = scaler.transform(bk_gp_df_for_ml)

    ### Clustering
    kmeans = KMeans(n_clusters = num_clusters, random_state = 0)
    clusters = kmeans.fit(bk_gp_df_for_ml_scaled)
    bk_gp_df_for_ml['cluster'] = pd.Series(clusters.labels_, index = bk_gp_df_for_ml.index)

    cluster_centers_raw = scaler.inverse_transform(kmeans.cluster_centers_)
    cluster_centers = []
    for i, cl_center in zip(range(num_clusters), cluster_centers_raw):
        cluster_centers.append(np.append([i], cl_center))
    cluster_centers = np.asarray(cluster_centers)
    
    # check the 'distribution' of clusters
    bk_gp_df_clustered = bk_gp_df_for_ml.copy()
    bk_gp_df_clustered['cluster'].value_counts()

    # predict using the values given
    val_df = pd.DataFrame(val_list).T
    val_transformed = scaler.transform(val_df)
    cluster_val = kmeans.predict(val_transformed)[0]

    # prepare the data with GEOID
    bk_gp_df_clustered.reset_index(inplace = True)
    bk_gp_df.reset_index(inplace = True)

    bk_gp_df_clustered_w_geo = bk_gp_df_clustered[['GEOID', 'cluster']].merge(bk_gp_df)

    # make dataframe as geodataframe
    bk_gp_df_clustered_w_geo = GeoDataFrame(bk_gp_df_clustered_w_geo, geometry = bk_gp_df_clustered_w_geo['geometry'])
    
    # return the data
    return bk_gp_df_clustered_w_geo, cluster_centers, cluster_val
