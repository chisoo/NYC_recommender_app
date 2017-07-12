from flask import Flask, render_template, request, redirect
import pickle

from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler

import geopandas as gpd
from geopandas import GeoDataFrame

import numpy as np
import pandas as pd

from bokeh.io import show
from bokeh.plotting import figure, save, output_file
from bokeh.models import ColumnDataSource, HoverTool, LogColorMapper
from bokeh.embed import components

from bokeh_helper import setColumnDataSource
from cluster_block_groups import cluster_block_groups

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
			'murder/manslaughter/homicide', 'rape/sex crime', 'robbery', 
			'assault', 'larceny', 'burglary', 'arson', 'theft', 'harrassment', 
			'drug', 'weapon', 'good trees']:
		if request.form.get(char): 
			char_chosen_list.append(char)
	return render_template('picked_chars.html', char_chosen_list = char_chosen_list)

@app.route('/recommendations', methods = ['POST'])
def recommendations():
	# read in the dataframe prepared for the graph
	with open('{}bk_gp_df_for_graph'.format(data_path), 'rb') as file_obj: 
		bk_gp_df_for_graph = pickle.load(file_obj)

	# get the feature_list and val_list from user input
	picked_vals_results = request.form
	feature_list = [k for k, v in picked_vals_results.items()]
	val_list = [int(v) for k, v in picked_vals_results.items()]

	num_cluster = 5
	cluster5, cluster_centers, cluster_val = \
		cluster_block_groups(bk_gp_df_for_graph, num_cluster, feature_list, val_list)

	cluster_df = cluster5[cluster5['cluster'] == 1].copy()
	cluster_centers = cluster_centers.astype(int).astype(str)

	with open('{}nynta_shape_df'.format(data_path), 'rb') as file_obj: 
		boundary_df = pickle.load(file_obj)

	# setup the list for hover
	hover_list = [("Neighborhood", "@NTAName")]
	hover_dict = {'med_hhld_inc': 'median income', 
				  'white_only_pct': 'white household', 
				  'black_only_pct': 'black household', 
				  'asian_only_pct': 'asian household', 
				  'mixed_races_pct': 'mixed race household', 
				  'hhld_size_all': 'household size',
				  'noise_res': 'noise complaint (residential)', 
				  'good trees': 'number of healthy trees'}
	for item in feature_list:  
		if item in hover_dict.keys():
			hover_list.append((hover_dict[item], "@{"+item+"}"))
		else: 
			hover_list.append((item, "@{"+item+"}"))
	print(hover_list)

	# prepare column data source
	cluster_df_vars = feature_list + ['lon', 'lat', 'NTAName']
	cluster_source = setColumnDataSource(cluster_df, cluster_df_vars)
	nynta_source = setColumnDataSource(boundary_df, ['lon', 'lat'])

	feature_list = np.append(['Group'], feature_list)
	val_list = np.append(['Desired'], val_list)
	picked_vals_kv = [feature_list, val_list]

	# initialize the figure
	cluster_plot = figure()

	# plot the cluster and boundary
	cluster_plot.patches('lon', 'lat', fill_color = None, line_color = 'black', 
				source = nynta_source, line_width = 1, name = 'nynta')
	cluster_plot.patches('lon', 'lat', fill_color = 'blue', alpha = 0.5, 
				source = cluster_source, name = 'cluster')

	# add hover tool
	hover = HoverTool(names = ['cluster'])
	hover.tooltips = hover_list
	cluster_plot.add_tools(hover)

	script, div = components(cluster_plot)

	return render_template("recommendations.html", script = script, div = div, 
							picked_vals_kv = picked_vals_kv, num_cluster = num_cluster, 
							cluster_centers = cluster_centers, cluster_val = cluster_val)  

if __name__ == '__main__':
	app.run(port=33507)
