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
from bokeh.plotting import figure, save
from bokeh.models import ColumnDataSource, HoverTool, LogColorMapper

from bokeh_helper import setColumnDataSource

app = Flask(__name__)

data_path = '../Data/'

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

def load_boundary_df():
	with open('{}nynta_shape_df'.format(data_path), 'rb') as file_obj: 
		boundary_df = pickle.load(file_obj)
	return boundary_df

# using PatchCollections
def draw_PatchCollections(geo_df, num_cluster, feature_list, cluster_val):
	boundary_df = load_boundary_df()

	geo_df_val = geo_df[geo_df['cluster'] == int(cluster_val)].copy()

	color_dict = {0: 'blue', 1: 'green', 2: 'yellow', 3: 'red', 4: 'pink'}
	geo_df_val['color'] = gep_df_val['cluster'].apply(lambda x: color_dict[x])

	cluster_source = setColumnDataSource(geo_df_val, ['lon', 'lat', 'color'])
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
	
if __name__ == '__main__':
	app.run(port=5000)
