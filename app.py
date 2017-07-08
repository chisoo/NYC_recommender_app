from flask import Flask, render_template, request, redirect
import pickle

from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler

import geopandas as gpd
from geopandas import GeoDataFrame

import numpy as np
import pandas as pd

# import matplotlib.pyplot as plt
# from descartes import PolygonPatch
# from matplotlib.patches import Polygon as mpl_Polygon
# from matplotlib.collections import PatchCollection
# import matplotlib

from bokeh.io import show
from bokeh.plotting import figure, save, output_file
from bokeh.models import ColumnDataSource, HoverTool, LogColorMapper
from bokeh.embed import components

from bokeh_helper import setColumnDataSource

app = Flask(__name__)

data_path = 'Data/'

@app.route('/')
def index():
	if request.method == 'GET':
		return render_template('index.html')

@app.route('/index', methods = ['POST'])
def picked_char():
	char_chosen_list = []
	for char in ['med_hhld_inc', 'white_only_pct', 'black_only_pct', 
			'asian_only_pct', 'mixed_races_pct', 'hhld_size_all', 'noise_res', 
			'assault', 'drug', 'harrassment', 'rape_sex_crime', 'robbery', 
			'theft', 'weapon', 'healthy_trees']:
		if request.form.get(char): 
			char_chosen_list.append(request.form.get(char))
	return render_template('picked_chars.html', char_chosen_list = char_chosen_list)

@app.route('/picked_vals', methods = ['POST'])
def picked_vals():
	picked_vals_results = request.form
	return render_template("picked_vals.html", picked_vals_results = picked_vals_results)

@app.route('/cluster_graph')
# using PatchCollections
def cluster_graph():
	with open('{}nynta_shape_df'.format(data_path), 'rb') as file_obj: 
		boundary_df = pickle.load(file_obj)

	with open('{}cluster5'.format(data_path), 'rb') as file_obj: 
		cluster5 = pickle.load(file_obj)

	cluster_df = cluster5[cluster5['cluster'] == 1].copy()

	cluster_source = setColumnDataSource(cluster_df, ['lon', 'lat'])
	nynta_source = setColumnDataSource(boundary_df, ['lon', 'lat', 'NTAName'])

	# initialize the figure
	cluster_plot = figure()

	# plot the cluster and boundary
	cluster_plot.patches('lon', 'lat', fill_color = 'blue', alpha = 0.5, source = cluster_source)
	cluster_plot.patches('lon', 'lat', fill_color = None, line_color = 'black', 
				source = nynta_source, line_width = 1)

	# add hover tool
	hover = HoverTool()
	hover.tooltips = [("Neighborhood", "@NTAName")]
	cluster_plot.add_tools(hover)

	script, div = components(cluster_plot)

	return render_template("cluster_graph.html", script = script, div = div)

@app.route('/cluster')
def cluster():
	return render_template("cluster.html")

@app.route('/clusterr')
def clusterr():
	return render_template("clusterr.html")

@app.route('/ccluster')
def ccluster():
	return render_template("ccluster.html")

@app.route('/cclusterr')
def cclusterr():
	return render_template("cclusterr.html")

def cluster_block_groups():
    num_clusters = 20
    picked_vals_results = request.form
    feature_list = [k for k, v in picked_vals_results.items()]
    val_list = [v for k, v in picked_vals_results.items()]
    """
    Parameters
    ----------
    num_clusters (int)
    feature_list (list): list of variables to use in the clustering
    val_list (list): list of values for each variables the user chose
    """
    # read in data
    with open('{}bk_gp_df_for_graph'.format(data_path), 'rb') as file_obj:
        bk_gp_df = pickle.load(file_obj)

    ### prepare data for clustering
    bk_gp_df.set_index('GEOID', inplace = True)
    bk_gp_df.head(3)

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

    # check the 'distribution' of clusters
    bk_gp_df_clustered = bk_gp_df_for_ml.copy()
    bk_gp_df_clustered['cluster'].value_counts()

    # predict using the values given
    val_df = pd.DataFrame(val_list).T
    val_transformed = scaler.transform(val_df)
    cluster_val = kmeans.predict(val_transformed)

    # prepare the data with GEOID
    bk_gp_df_clustered.reset_index(inplace = True)
    bk_gp_df.reset_index(inplace = True)

    bk_gp_df_clustered_w_geo = bk_gp_df_clustered[['GEOID', 'cluster']].merge(bk_gp_df)

    # make dataframe as geodataframe
    bk_gp_df_clustered_w_geo = GeoDataFrame(bk_gp_df_clustered_w_geo, geometry = bk_gp_df_clustered_w_geo['geometry'])

    # return the data
    return render_template("cluster_old.html")

if __name__ == '__main__':
	app.run(port=5000)
