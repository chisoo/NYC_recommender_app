from flask import Flask, render_template, request, redirect
import pickle

from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import euclidean_distances

import geopandas as gpd
from geopandas import GeoDataFrame

import numpy as np
import pandas as pd
import os

from bokeh.io import show
from bokeh.plotting import figure, save, output_file
from bokeh.models import ColumnDataSource, HoverTool, LogColorMapper
from bokeh.embed import components
from bokeh.resources import CDN

from bokeh_helper import setColumnDataSource
from find_closest_bk_gp import find_closest_bk_gp
from draw_example_maps import draw_bk_gp_family_hhld, draw_nta_family_hhld

app = Flask(__name__)

data_path = 'Data/'

app.var_dict = {'med_hhld_inc':'Median household income', 
				'hhld_size_all': 'Household Size', 
				'noise_res': 'Noise complaint (residential)', 
				'rodent': 'Rodent complaint', 
				'murder_manslaughter_homicide': 'Murder/Manslaughter/Homicide', 
				'rape_sex_crime': 'Rape/Sex Crime', 
				'robbery': 'Robbery', 
				'assault': 'Assault', 
				'larceny': 'Larceny', 
				'burglary': 'Burglary', 
				'arson': 'Arson', 
				'theft': 'Theft', 
				'harrassment': 'Harrassment', 
				'drug': 'Drug', 
				'weapon': 'Weapon', 
				'good_trees': 'Number of healthy trees', 
				'med_gross_rent': 'Median gross rent', 
				'med_num_rooms': 'Median number of rooms', 
				'num_lines': 'Number of subway lines', 
				'num_food_venues': 'Number of food venues'}
app.char_to_avoid_list = []

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/pick_chars', methods = ['POST'])
def pick_chars():
	if request.method == 'POST':
		return render_template('pick_chars.html')

@app.route('/data_source', methods = ['POST'])
def data_source():
	if request.method == 'POST':
		return render_template('data_source.html')
		
@app.route('/picked_chars', methods = ['POST'])
def picked_chars():
	char_chosen_list = []
	for char in ['med_hhld_inc', 'hhld_size_all', 'good_trees', 'med_gross_rent',
			     'med_num_rooms', 'num_lines', 'num_food_venues']:
		if request.form.get(char): 
			char_chosen_list.append(char)
	for char in ['noise_res', 'rodent', 'murder_manslaughter_homicide', 
				 'rape_sex_crime', 'robbery', 'assault', 'larceny', 'burglary', 
				 'arson', 'theft', 'harrassment', 'drug', 'weapon']: 
		if request.form.get(char): 
			app.char_to_avoid_list.append(char)
	return render_template('picked_chars.html', char_chosen_list = char_chosen_list, 
							var_dict = app.var_dict)

# example plots for viz miniproject
@app.route('/example_plot1')
def example_plot1():
	return render_template('family_hhld_bk_gp_plot.html')

@app.route('/example_plot2')
def example_plot2():
	return render_template('family_hhld_nta_plot.html')

@app.route('/example_plot3')
def example_plot3():
	return render_template('hist_example.html')

@app.route('/recommendations', methods = ['POST'])
def recommendations():
	# get the feature_list and val_list from user input
	picked_vals_results = request.form
	feature_list = [k for k, v in picked_vals_results.items()] 
	val_list = [int(v) for k, v in picked_vals_results.items()]
	for item in app.char_to_avoid_list: 
		feature_list.append(item)
		val_list.append(0)

	# read in the dataframe prepared for the graph
	with open('{}bk_gp_df_for_graph'.format(data_path), 'rb') as file_obj: 
		bk_gp_df_for_graph = pickle.load(file_obj)

	num_to_find = 5
	closest_bk_gp_df = \
		find_closest_bk_gp(bk_gp_df_for_graph, num_to_find, feature_list, val_list)

	# merge in zillow neighborhood for each GEOID
	with open('{}zillow_df_w_geoid'.format(data_path), 'rb') as file_obj: 
		zillow_df_w_geoid = pickle.load(file_obj)
	closest_bk_gp_df = closest_bk_gp_df\
						.merge(zillow_df_w_geoid[['GEOID', 'Name', 'Boro']].copy())\
						.sort_values('rank')

	# save rank and zillow neighborhood name as dictionary
	rank_dict = closest_bk_gp_df[['rank', 'GEOID']].set_index('rank').to_dict()
	vars_for_result_table = ['GEOID', 'Name', 'Boro'] + feature_list
	zillow_dict = closest_bk_gp_df[vars_for_result_table].set_index('GEOID').to_dict()

	# read in zillow shape file for boundary
	with open('{}zillow_shape_df'.format(data_path), 'rb') as file_obj: 
		zillow_shape_df = pickle.load(file_obj)

	# setup the list for hover
	hover_list = [("Rank", "@rank"), ("Neighborhood", "@Name")]
	hover_dict = {'med_hhld_inc': 'median income', 
				  'hhld_size_all': 'household size',
				  'noise_res': 'noise complaint (residential)', 
				  'rodent': 'rodent complaint', 
				  'good_trees': 'number of healthy trees', 
				  'num_lines': 'number of subway lines', 
				  'num_venues': 'number of any venues', 
				  'num_food_venues': 'number of food venues'}

	for item in feature_list:  
		if item in hover_dict.keys():
			hover_list.append((hover_dict[item], "@{"+item+"}"))
		else: 
			hover_list.append((item, "@{"+item+"}"))

	# prepare column data source
	bk_gp_df_vars = feature_list + ['rank', 'lon', 'lat', 'Name']
	bk_gp_source = setColumnDataSource(closest_bk_gp_df, bk_gp_df_vars)
	zillow_source = setColumnDataSource(zillow_shape_df, ['lon', 'lat'])

	picked_vals_kv = [['Group'] + feature_list, ['Desired'] + val_list]

	# initialize the figure
	bk_gp_plot = figure()

	# plot grid
	bk_gp_plot.patches('lon', 'lat', fill_color = 'grey', alpha = 0.2, 
					   line_color = 'black', line_width = 0.5, 
					   source = zillow_source, name = 'zillow')
	bk_gp_plot.patches('lon', 'lat', fill_color = 'blue', 
					   source = bk_gp_source, name = 'bk_gp')

	# add hover tool
	hover = HoverTool(names = ['bk_gp'])
	hover.tooltips = hover_list
	bk_gp_plot.add_tools(hover)

	script, div = components(bk_gp_plot)

	return render_template("recommendations.html", script = script, div = div,  
							picked_vals_kv = picked_vals_kv, num_to_find = num_to_find, 
							rank_dict = rank_dict, zillow_dict = zillow_dict, 
							feature_list = feature_list)  

if __name__ == '__main__':
	app.run(port=33507)
