from flask import Flask, render_template, request, redirect
import pickle

from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler

import geopandas as gpd
from geopandas import GeoDataFrame

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
from descartes import PolygonPatch
from matplotlib.patches import Polygon as mpl_Polygon
from matplotlib.collections import PatchCollection
import matplotlib

app = Flask(__name__)

data_path = '../Data/'

@app.route('/')
def main():
	return redirect('/index')

@app.route('/index', methods = ['GET', 'POST'])
def index():
	if request.method == 'GET':
  		return render_template('index.html')
	else: 
		char_chosen_list = []
		for char in ['med_hhld_inc', 'white_only_pct', 'black_only_pct', 
				'asian_only_pct', 'mixed_races_pct', 'hhld_size_all', 'noise_res', 
				'assault', 'drug', 'harrassment', 'rape_sex_crime', 'robbery', 
				'theft', 'weapon', 'healthy_trees']:
			if request.form.get(char): 
				char_chosen_list.append(request.form.get(char))
		return render_template('picked_chars.html', char_chosen_list = char_chosen_list)
  		
@app.route('/picked_vals', methods = ['POST', 'GET'])
def picked_vals():
	if request.method == 'POST':
		picked_vals_results = request.form
		return render_template("picked_vals.html", picked_vals_results = picked_vals_results)

def cluster_block_groups(num_clusters, feature_list, val_list):
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
	return bk_gp_df_clustered_w_geo, cluster_val

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
	print('Please choose the boundary to use (boro/nynta).')
	boundary_ans = input()
	with open('{}{}_shape_df'.format(data_path, boundary_ans), 'rb') as file_obj: 
		boundary_df = pickle.load(file_obj)
	return boundary_ans, boundary_df

# using PatchCollections
def draw_PatchCollections(geo_df, num_cluster, feature_list, cluster_val):
	boundary_ans, boundary_df = load_boundary_df()

	geo_df_val = geo_df[geo_df['cluster'] == int(cluster_val)].copy()

	color_dict = {0: 'blue', 1: 'green', 2: 'yellow', 3: 'red', 4: 'pink'}

	def polygon_to_patches(geo_df):
		for i, row in geo_df.iterrows():
	        m_polygon = row['geometry']
			poly = []
			if m_polygon.geom_type == 'MultiPolygon':
				for m_poly in m_polygon: 
	 				poly.append(PolygonPatch(m_poly))
			else: 
				poly.append(PolygonPatch(m_polygon))
			geo_df.set_value(i, 'mpl_polygon', poly)
		return geo_df

	geo_df_val = polygon_to_patches(geo_df_val)
	boundary_df = polygon_to_patches(boundary_df)

	fig = plt.figure(figsize = (15, 12))
	ax = fig.gca()

	# draw boundary
	for i, row in boundary_df.iterrows():
		p = PatchCollection(row['mpl_polygon'], facecolors = 'None', edgecolors = 'k')
		ax.add_collection(p)
	ax.autoscale_view()

    # draw clusters
	for i, row in geo_df_val.iterrows():
		p = PatchCollection(row['mpl_polygon'], facecolors = 'blue', edgecolors = 'None')
		ax.add_collection(p)
	ax.autoscale_view()

	plt.title('{} Clusters, {} as boundary:{}'.format(num_cluster, boundary_ans, feature_list))
	plt.savefig('{}{} Clusters vs {}.png'.format(graph_path, num_cluster, boundary_ans));

	plt.show()

if __name__ == '__main__':
	app.run(port=33507)
