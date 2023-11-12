import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import geopandas as gpd
import arrow
from shapely import wkb,wkt

from testing.utils.dashboard_shared import Table

class Data:
	def __init__(self):
		boundaries_df = Table('CB_gis_boundaries').df
		self.boundaries = gpd.GeoDataFrame(boundaries_df,geometry=boundaries_df['geometry'].apply(wkt.loads),crs="EPSG:4326")
		
		
		wells_df = Table('CB_well_info').df
		
		self.well_info = gpd.GeoDataFrame(wells_df,geometry=wells_df['geometry'].apply(wkt.loads),crs="EPSG:4326")
		# .pipe(lambda df: df.loc[df['DMS_Site_ID'].isin(wells)])
		# wells_df = Table(table_name).df
		
		self.well_depth_to_water = Table('CB_well_water_levels').df.dropna(subset=['meas_depth'])
		self.well_depth_to_water['date'] = self.well_depth_to_water['meas_date'].apply(lambda x: arrow.get(x).naive)
		self.well_depth_to_water = self.well_depth_to_water.sort_values('date')
		
		
		# .pipe(lambda df: df.loc[df['dms_site_id'].isin(wells)])
		self.well_extractions = Table('CB_well_production_monthly_af').df.sort_values(['year','month'])

class Wells(Data):
	def __init__(self,wells):
		super().__init__()
		select_wells = lambda df: df.loc[df['dms_site_id'].isin(wells)]
		self.well_info = self.well_info.pipe(select_wells)
		self.well_depth_to_water = self.well_depth_to_water.pipe(select_wells)
		self.well_extractions = self.well_extractions.pipe(select_wells)