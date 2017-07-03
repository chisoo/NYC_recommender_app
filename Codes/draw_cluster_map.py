import pickle

import geopandas as gpd
from geopandas import GeoDataFrame

import matplotlib.pyplot as plt
from IPython.display import display

from cluster_block_groups import cluster_block_groups

# set the paths for data and graphs
data_path = "../../Data/"
graph_path = "../Graphs/From App/"

### first, write helper functions
def take_feature_input():
    # take the features
    possible_feature_list = ['med_hhld_inc', 'white_only_pct', 'black_only_pct', 
                'asian_only_pct', 'mixed_races_pct', 'hhld_size_all', 'same_house_pct', 
                'med_gross_rent', 'Noise - Residential', 'assault', 'drug', 
                'harrassment', 'larceny', 'murder/manslaughter/homicide', 
                'rape/sex crime', 'robbery', 'theft', 'weapon', 'good trees']
    feature_list = []

    print("Please enter the features you want to include. Please enter one at a time.")
    print("Here is the list of possible features to use:")
    for item in possible_feature_list:
        print(item)
    print("----------")

    ans = input()
    while ans != "":
        feature_list.append(ans)
        ans = input()
        
    print("features to be included:", feature_list)
    return feature_list

def load_boundary_df():
    print('Please choose the boundary to use (boro/nynta).')
    boundary_ans = input()
    if boundary_ans == "boro":    
        with open('{}pickled_data/boro_shape_df'.format(data_path), 'rb') as file_obj: 
            boundary_df = pickle.load(file_obj)

    elif boundary_ans == 'nynta':    
        with open('{}pickled_data/nynta_shape_df'.format(data_path), 'rb') as file_obj: 
            boundary_df = pickle.load(file_obj)

    return boundary_ans, boundary_df

def draw_map(geo_df):
    boundary_ans, boundary_df = load_boundary_df()
    base = boundary_df.plot(figsize = (16, 12), color = 'white')
    geo_df.plot(ax = base, column = 'cluster', figsize = (16, 12), cmap = 'viridis', 
                                  categorical = True, legend = True, edgecolor = 'none')
    plt.title('{} Clusters, {} as boundary:{}'.format(num_cluster, boundary_ans, feature_list))
    plt.savefig('{}{} Clusters vs {}.png'.format(graph_path, num_cluster, boundary_ans));
    plt.show()

###
if __name__ == '__main__':
    ##########
    ### read in and prepare data
    ##########

    # take the features
    feature_list = take_feature_input()

    ### Get the user input for the number of clusters
    print("\nHow many clusters do you want?")
    print("----------")

    num_cluster = int(input())

    ##########
    ### cluster
    ##########
    bk_gp_df_clustered_w_geo = cluster_block_groups(num_cluster, feature_list)
    print('clustering done')

    # show the means for each table
    display(bk_gp_df_clustered_w_geo.pivot_table(feature_list, index = 'cluster').T)

    ##########
    ### save data
    ##########
    with open('{}clustered_data/cluster{}'.format(data_path, num_cluster), 'wb') as file_obj:
        pickle.dump(bk_gp_df_clustered_w_geo, file_obj)

    ##########
    ### ask the user whether they want a map - if yes, draw cluster map
    ##########
    print('\nDo you want to see a map? (y/n)')
    print("----------")

    ans = input()
    if ans == 'y':
        draw_map(bk_gp_df_clustered_w_geo)

