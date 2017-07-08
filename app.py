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
			'assault', 'drug', 'harrassment', 'rape_sex_crime', 'robbery', 
			'theft', 'weapon', 'good trees']:
		if request.form.get(char): 
			char_chosen_list.append(char)
	return render_template('picked_chars.html', char_chosen_list = char_chosen_list)

@app.route('/cluster_graph', methods = ['POST'])
def cluster_graph():
	# read in the dataframe prepared for the graph
	with open('{}bk_gp_df_for_graph'.format(data_path), 'rb') as file_obj: 
		bk_gp_df_for_graph = pickle.load(file_obj)

	# get the feature_list and val_list from user input
	picked_vals_results = request.form
	feature_list = [k for k, v in picked_vals_results.items()]
	val_list = [float(v) for k, v in picked_vals_results.items()]

	cluster5, cluster_val = \
		cluster_block_groups(bk_gp_df_for_graph, 5, feature_list, val_list)

	with open('{}nynta_shape_df'.format(data_path), 'rb') as file_obj: 
		boundary_df = pickle.load(file_obj)

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

	return render_template("cluster_graph.html", picked_vals_results = picked_vals_results, 
							script = script, div = div) 

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


if __name__ == '__main__':
	app.run(port=5000)
