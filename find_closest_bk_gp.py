# setup
import numpy as np
import pandas as pd
import pickle

from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import euclidean_distances

data_path = 'Data/'

def find_closest_bk_gp(df, num_to_find, feature_list, val_list): 
    """
    Parameters
    ----------
    bk_gp_df (DataFrame)
    num_to_find (int)
    feature_list (list): list of variables to use in the clustering
    val_list (list): list of values for each variables the user chose

    OUTPUT
    ----------
    closest_bk_gp_df: DataFrame with the closest block groups
    """

    bk_gp_df = df.set_index('GEOID')[feature_list].copy()
    bk_gp_df.drop_duplicates(inplace = True)

    # create a DataFrame with given values
    val_df = pd.DataFrame(val_list).T
    val_df.columns = feature_list
    val_df.index = ['val_given']

    # combine the two dataframes
    bk_gp_df = bk_gp_df.append(val_df)

    # scale the data
    scaler = MinMaxScaler()
    scaler.fit(bk_gp_df)
    bk_gp_df_scaled = scaler.transform(bk_gp_df)
    bk_gp_df_scaled = pd.DataFrame(bk_gp_df_scaled, 
                                   columns = bk_gp_df.columns, 
                                   index = bk_gp_df.index)

    # calculate distance
    dist = euclidean_distances(bk_gp_df_scaled)
    dist_series = pd.DataFrame(dist, index = bk_gp_df.index, 
                               columns = bk_gp_df.index)['val_given']
    rank_df = pd.DataFrame(dist_series.sort_values()[1:num_to_find + 1].index, 
                                columns = ['GEOID']).reset_index()
    rank_df.rename(columns = {'index': 'rank'}, inplace = True)
    rank_df['rank'] = rank_df['rank'] + 1

    closest_bk_gp_df = df.merge(rank_df).copy()

    return closest_bk_gp_df

if __name__ == '__main__': 
    with open('{}bk_gp_df_for_graph'.format(data_path), 'rb') as file_obj: 
        bk_gp_df_for_graph = pickle.load(file_obj)

    closest_bk_gp_df = find_closest_bk_gp(bk_gp_df_for_graph, 5, 
                                   ['med_hhld_inc', 'num_lines', 'num_food_venues'], 
                                   [100000, 1, 20])
    print('shape: {}'.format(closest_bk_gp_df.shape))
    print(closest_bk_gp_df[['rank', 'GEOID']])