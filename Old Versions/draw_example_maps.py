import pickle
import geopandas as gpd
from geopandas import GeoDataFrame

from bokeh.io import show
from bokeh.plotting import figure, save, output_file
from bokeh.models import ColumnDataSource, HoverTool, LogColorMapper
from bokeh.embed import components

from bokeh_helper import setColumnDataSource

data_path = 'Data/'

def prepare_boro_src():	
	with open('{}boro_shape_df'.format(data_path), 'rb') as file_obj:
		boro_shape_df = pickle.load(file_obj)
	return setColumnDataSource(boro_shape_df, ['lon', 'lat'])

def prepare_nynta_src():	
	with open('{}nynta_shape_df'.format(data_path), 'rb') as file_obj:
		nynta_shape_df = pickle.load(file_obj)
	return setColumnDataSource(nynta_shape_df, ['lon', 'lat'])

# block group
def draw_bk_gp_family_hhld():
	with open('{}hhld_type_bk_gp_df_geo'.format(data_path), 'rb') as file_obj:
		hhld_type_bk_gp_df = pickle.load(file_obj)

	family_hhld_bk_gp_cds_list = ['GEOID', 'NAME', 'lon', 'lat', 'family_hhld_pct_grp', 'family_hhld_colors']

	hhld_type_bk_gp_df_m = hhld_type_bk_gp_df[hhld_type_bk_gp_df['family_hhld_pct_grp'] == 'missing'].copy()
	hhld_type_bk_gp_df_0 = hhld_type_bk_gp_df[hhld_type_bk_gp_df['family_hhld_pct_grp'] == '0'].copy()
	hhld_type_bk_gp_df_70 = hhld_type_bk_gp_df[hhld_type_bk_gp_df['family_hhld_pct_grp'] == '<-70'].copy()
	hhld_type_bk_gp_df_80 = hhld_type_bk_gp_df[hhld_type_bk_gp_df['family_hhld_pct_grp'] == '70<-80'].copy()
	hhld_type_bk_gp_df_90 = hhld_type_bk_gp_df[hhld_type_bk_gp_df['family_hhld_pct_grp'] == '80<-90'].copy()
	hhld_type_bk_gp_df_100 = hhld_type_bk_gp_df[hhld_type_bk_gp_df['family_hhld_pct_grp'] == '90<-100'].copy()

	hhld_type_bk_gp_family_hhld_source_m = setColumnDataSource(hhld_type_bk_gp_df_m, family_hhld_bk_gp_cds_list)
	hhld_type_bk_gp_family_hhld_source_0 = setColumnDataSource(hhld_type_bk_gp_df_0, family_hhld_bk_gp_cds_list)
	hhld_type_bk_gp_family_hhld_source_70 = setColumnDataSource(hhld_type_bk_gp_df_70, family_hhld_bk_gp_cds_list)
	hhld_type_bk_gp_family_hhld_source_80 = setColumnDataSource(hhld_type_bk_gp_df_80, family_hhld_bk_gp_cds_list)
	hhld_type_bk_gp_family_hhld_source_90 = setColumnDataSource(hhld_type_bk_gp_df_90, family_hhld_bk_gp_cds_list)
	hhld_type_bk_gp_family_hhld_source_100 = setColumnDataSource(hhld_type_bk_gp_df_100, family_hhld_bk_gp_cds_list)

	src_list = [hhld_type_bk_gp_family_hhld_source_m, hhld_type_bk_gp_family_hhld_source_0, 
				hhld_type_bk_gp_family_hhld_source_70, hhld_type_bk_gp_family_hhld_source_80, 
				hhld_type_bk_gp_family_hhld_source_90, hhld_type_bk_gp_family_hhld_source_100]
	legend_list = ['missing', '0%', '<-70%', '70%<-80%', '80%<-90%', '90%<-100%']

	family_hhld_bk_gp_plot = figure()
	for src, lgnd in zip(src_list, legend_list):
		family_hhld_bk_gp_plot.patches('lon', 'lat', alpha = 0.5, source = src, 
									   line_color = None, fill_color = 'family_hhld_colors', 
									   name = 'block_group', legend = lgnd)

	boundary_source = prepare_nynta_src()
	family_hhld_bk_gp_plot.patches('lon', 'lat', source = boundary_source, line_color = 'black', line_width = 1, 
								   fill_color = None, name = 'boundary')

	family_hhld_bk_gp_plot.legend.location = "top_left"

	# add hover tool
	hover = HoverTool(names = ['block_group'])
	hover.tooltips = [('Block Group Name', '@{NAME}'), ('family household', '@{family_hhld_pct_grp}')]
	family_hhld_bk_gp_plot.add_tools(hover)

	return components(family_hhld_bk_gp_plot)

# nta
def draw_nta_family_hhld():
	with open('{}hhld_type_nta_df_geo'.format(data_path), 'rb') as file_obj:
		hhld_type_nta_df = pickle.load(file_obj)

	family_hhld_nta_cds_list = ['NTACode', 'NTAName', 'lon', 'lat', 'family_hhld_pct_grp', 'family_hhld_colors']

	hhld_type_nta_df_0 = hhld_type_nta_df[hhld_type_nta_df['family_hhld_pct_grp'] == '0'].copy()
	hhld_type_nta_df_70 = hhld_type_nta_df[hhld_type_nta_df['family_hhld_pct_grp'] == '<-70'].copy()
	hhld_type_nta_df_80 = hhld_type_nta_df[hhld_type_nta_df['family_hhld_pct_grp'] == '70<-80'].copy()
	hhld_type_nta_df_90 = hhld_type_nta_df[hhld_type_nta_df['family_hhld_pct_grp'] == '80<-90'].copy()
	hhld_type_nta_df_100 = hhld_type_nta_df[hhld_type_nta_df['family_hhld_pct_grp'] == '90<-100'].copy()

	hhld_type_nta_family_hhld_source_0 = setColumnDataSource(hhld_type_nta_df_0, family_hhld_nta_cds_list)
	hhld_type_nta_family_hhld_source_70 = setColumnDataSource(hhld_type_nta_df_70, family_hhld_nta_cds_list)
	hhld_type_nta_family_hhld_source_80 = setColumnDataSource(hhld_type_nta_df_80, family_hhld_nta_cds_list)
	hhld_type_nta_family_hhld_source_90 = setColumnDataSource(hhld_type_nta_df_90, family_hhld_nta_cds_list)
	hhld_type_nta_family_hhld_source_100 = setColumnDataSource(hhld_type_nta_df_100, family_hhld_nta_cds_list)

	src_list = [hhld_type_nta_family_hhld_source_0, 
			hhld_type_nta_family_hhld_source_70, hhld_type_nta_family_hhld_source_80, 
			hhld_type_nta_family_hhld_source_90, hhld_type_nta_family_hhld_source_100]
	legend_list = ['0', '<-70', '70<-80', '80<-90', '90<-100']

	family_hhld_nta_plot = figure()
	for src, lgnd in zip(src_list, legend_list):
		family_hhld_nta_plot.patches('lon', 'lat', alpha = 0.5, source = src, 
									   line_color = None, fill_color = 'family_hhld_colors', 
									   name = 'nta', legend = lgnd)

	boundary_source = prepare_nynta_src()
	family_hhld_nta_plot.patches('lon', 'lat', source = boundary_source, line_color = 'black', line_width = 1, 
								   fill_color = None, name = 'boundary')

	family_hhld_nta_plot.legend.location = "top_left"

	# add hover tool
	hover = HoverTool(names = ['nta'])
	hover.tooltips = [('NTA Name', '@{NTAName}'), ('family household', '@{family_hhld_pct_grp}')]
	family_hhld_nta_plot.add_tools(hover)    

	return components(family_hhld_nta_plot)	

