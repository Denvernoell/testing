import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import geopandas as gpd
import arrow
from shapely import wkb,wkt

from utils.dashboard_shared import Table



from pathlib import Path
import polars as pl
data_path = Path("utils")
wq_systems = pl.read_parquet(data_path / "wq_systems.parquet").to_pandas()


class Data:
	def __init__(self):
		boundaries_df = Table('CB_gis_boundaries').df
		self.boundaries = gpd.GeoDataFrame(boundaries_df,geometry=boundaries_df['geometry'].apply(wkt.loads),crs="EPSG:4326")
		wells_df = Table('CB_well_info').df
		self.well_info = gpd.GeoDataFrame(wells_df,geometry=wells_df['geometry'].apply(wkt.loads),crs="EPSG:4326")
		self.well_names = Table('CB_well_names').df
		
		# df['well_name'] = df['name'] + ' - (' + df['dms_site_id'] + ")"
		
		self.well_depth_to_water = Table('CB_well_water_levels').df.dropna(subset=['meas_depth']).assign(
			date = lambda df: df['meas_date'].apply(lambda x: arrow.get(x).naive)
		).sort_values('date')
		# self.well_depth_to_water['date'] = self.well_depth_to_water['meas_date'].apply(lambda x: arrow.get(x).naive)
		# self.well_depth_to_water = self.well_depth_to_water.sort_values('date')
		# self.well_depth_to_water = self.well_depth_to_water

		self.well_extractions = Table('CB_well_production_monthly_af').df
		# .assign(
		# 	date = lambda df: df['date'].apply(lambda x: arrow.get(x).naive)
		# ).sort_values(['date'])
		# self.well_extractions['date'] = self.well_extractions['date'].apply(lambda x: arrow.get(x).naive)
		# self.well_extractions = self.well_extractions

		self.well_water_quality =Table('CB_well_water_quality').df.assign(
			date = lambda df: df['date'].apply(lambda x: arrow.get(x).naive)
		).sort_values(['date'])
		# self.well_water_quality['date'] = self.well_water_quality['date'].apply(lambda x: arrow.get(x).naive)
		# self.well_water_quality = self.well_water_quality.sort_values(['date'])
		self.well_water_quality['constituent'] = self.well_water_quality['constituent'].str.replace('\n ','')
		self.well_water_quality['result'] = pd.to_numeric(self.well_water_quality['result'],errors='coerce')

	def filter_wells(self,wells):
		select_wells = lambda df: df.loc[df['dms_site_id'].isin(wells)]
		return {
		'well_info' : self.well_info.pipe(select_wells),
		'well_depth_to_water' : self.well_depth_to_water.pipe(select_wells),
		'well_extractions' : self.well_extractions.pipe(select_wells),
		'well_water_quality' : self.well_water_quality.pipe(select_wells),	
		}
	

		# return self
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


data = Data()















# import polars as pl
# from pathlib import Path
# # data_path = Path("data")
# data_path = Path(__file__).parent

# sdwis_data = pl.read_parquet(
# 	data_path.joinpath("sdwis_wq.parquet")
# 		).select(
# 			pl.col(pl.Utf8).str.strip()
# 			).with_columns(
# 				pl.col("Sample Date").str.strptime(pl.Date, fmt="%m-%d-%Y").alias("Date")
# 				).filter(
# 					pl.col('Date') > pl.date(2015,1,1)
# 							).with_columns(
# 								pl.col('Result').cast(pl.Float32,strict=True).fill_null(-1).alias("reading")
# 								).sort("Date", descending=False)


# def load_data(ps_codes,chemicals_to_check):
# 	return pl.read_parquet(
# 		data_path.joinpath("gsa_swrcb_wq.parquet")
# 		# ).filter(
# 		# 	pl.col('PS Code').str.strip().is_in(ps_codes)
# 			).select(
# 				pl.col(pl.Utf8).str.strip()
# 				).with_columns(
# 					pl.col("Sample Date").str.strptime(pl.Date, fmt="%m-%d-%Y").alias("Date")
# 					).filter(
# 						pl.col('Date') > pl.date(2015,1,1)
# 						# ).filter(
# 						# 	pl.col('Date') < pl.date(2022,1,1)
# 							# ).filter(
# 							# 	pl.col('Analyte Name').is_in(chemicals_to_check)
# 								# ).with_columns(
# 								# 	pl.col('Result').cast(pl.Float32,strict=True).fill_null(-1).alias("reading")
# 									).sort("Date", descending=True)