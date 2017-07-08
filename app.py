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

	color_dict = {0: 'blue', 1: 'green', 2: 'yellow', 3: 'red', 4: 'pink'}
	cluster5['color'] = cluster5['cluster'].apply(lambda x: color_dict[x])

	cluster_source = setColumnDataSource(cluster5, ['lon', 'lat', 'color'])
	nynta_source = setColumnDataSource(boundary_df, ['lon', 'lat'])

	# initialize the figure
	cluster_plot = figure()

	# plot the cluster and boundary
	cluster_plot.patches('lon', 'lat', fill_color = 'color', alpha = 0.5, source = cluster_source)
	cluster_plot.patches('lon', 'lat', fill_color = None, line_color = 'black', 
				source = nynta_source, line_width = 1)

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
	print("Please provide the values you prefer for each feature:")
	val_list = []
	for _, feature in enumerate(feature_list):
		print(feature)
		val = float(input())
		val_list.append(val)
	return feature_list, val_list


if __name__ == '__main__':
	app.run(port=5000)
