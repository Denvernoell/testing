import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import geopandas as gpd
import arrow
from shapely import wkb,wkt

from utils.dashboard_shared import Table
# from districts.cucamonga.figures import Map

class Data:
	def __init__(self):
		boundaries_df = Table('CB_gis_boundaries').df
		self.boundaries = gpd.GeoDataFrame(boundaries_df,geometry=boundaries_df['geometry'].apply(wkt.loads),crs="EPSG:4326")
		wells_df = Table('CB_well_info').df
		self.well_info = gpd.GeoDataFrame(wells_df,geometry=wells_df['geometry'].apply(wkt.loads),crs="EPSG:4326")
		self.well_names = Table('CB_well_names').df
		
		# df['well_name'] = df['name'] + ' - (' + df['dms_site_id'] + ")"
		
		self.well_depth_to_water = Table('CB_well_water_levels').df.dropna(subset=['meas_depth'])
		self.well_depth_to_water['date'] = self.well_depth_to_water['meas_date'].apply(lambda x: arrow.get(x).naive)
		self.well_depth_to_water = self.well_depth_to_water.sort_values('date')
		self.well_extractions = Table('CB_well_production_monthly_af').df
		self.well_extractions['date'] = self.well_extractions['date'].apply(lambda x: arrow.get(x).naive)
		self.well_extractions = self.well_extractions.sort_values(['date'])

		self.well_water_quality =Table('CB_well_water_quality').df 
		self.well_water_quality['date'] = self.well_water_quality['date'].apply(lambda x: arrow.get(x).naive)
		self.well_water_quality = self.well_water_quality.sort_values(['date'])
		self.well_water_quality['constituent'] = self.well_water_quality['constituent'].str.replace('\n ','')
		self.well_water_quality['result'] = pd.to_numeric(self.well_water_quality['result'],errors='coerce')



# Nitrate as N
#   (NO3-N)
# Nitrate as N (NO3-N)

class Wells(Data):
	def __init__(self,wells):
		super().__init__()
		select_wells = lambda df: df.loc[df['dms_site_id'].isin(wells)]
		self.well_info = self.well_info.pipe(select_wells)
		self.well_depth_to_water = self.well_depth_to_water.pipe(select_wells)
		self.well_extractions = self.well_extractions.pipe(select_wells)
		self.well_water_quality = self.well_water_quality.pipe(select_wells)

class Agency(Data):
	def __init__(self,agency):
		super().__init__()
		wells = self.well_names.loc[self.well_names['agency']==agency]['dms_site_id'].unique()
		select_wells = lambda df: df.loc[df['dms_site_id'].isin(wells)]
		self.well_info = self.well_info.pipe(select_wells)
		self.well_depth_to_water = self.well_depth_to_water.pipe(select_wells)
		self.well_extractions = self.well_extractions.pipe(select_wells)
		self.well_water_quality = self.well_water_quality.pipe(select_wells)