import pandas as pd
import plotly.express as px
import arrow
import geopandas as gpd
import leafmap.foliumap as leafmap
from shapely import wkb,wkt
import streamlit as st

from testing.utils.dashboard_shared import Table
from districts.cucamonga.general import Data


import matplotlib.pyplot as plt
class Map:
	def __init__(self):
		self.map = leafmap.Map(
			google_map="HYBRID",
			draw_control=False,
		)

	def add_boundaries(self,boundaries):	
		table_name = 'CB_gis_boundaries'
		boundaries_df = Table(table_name).df.pipe(lambda df: df.loc[df['name'].isin(boundaries)])

		# boundaries_df = boundaries.loc[boundaries['file_name'].isin(['Tranquillity Irrigation District',"Fresno Slough Water District"])]
		boundaries_gdf = gpd.GeoDataFrame(boundaries_df,geometry=boundaries_df['geometry'].apply(wkt.loads),crs="EPSG:4326")
		
		self.map.add_gdf(boundaries_gdf,layer_name="Boundaries",info_mode='on_click',)
	
	def add_wells(self,wells):
		table_name = 'CB_well_info'
		wells_df = Table(table_name).df.pipe(lambda df: df.loc[df['DMS_Site_ID'].isin(wells)])
		# wells_df = Table(table_name).df
		wells_gdf = gpd.GeoDataFrame(wells_df[['DMS_Site_ID','Monitor_By']]
			       ,geometry=wells_df['geometry'].apply(wkt.loads),crs="EPSG:4326")
		self.map.add_gdf(wells_gdf,layer_name="Wells",info_mode='on_hover',)
	
class Figure:
	def __init__(self,data):
		self.data = data
	
	def depth_to_water(self,df):
		self.fig = px.line()
		self.fig = px.scatter(df,x='meas_date',y='meas_depth',color='dms_site_id')
		self.fig.update_layout(
			title="Depth to Water",
			xaxis_title="Date",
			yaxis_title="Depth to Water (ft)",
			legend_title="Well",
			# connect lines
			hovermode="x unified",
			# hovermode="x",
		)
		# reverse
		self.fig.update_yaxes(autorange="reversed")
		self.fig.update_traces(mode="lines+markers")


	def mpl_depth_to_water(self,start_date=None,end_date=None):
		df = self.data.well_depth_to_water
		if start_date is not None:
			start_date = arrow.get(start_date).datetime
			df = df.loc[df['meas_date'] >= start_date]
		if end_date is not None:
			end_date = arrow.get(end_date).datetime
			df = df.loc[df['meas_date'] <= end_date]

		# df = df.loc[(df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date)]

		fig, ax = plt.subplots()
		# make 8.5x11
		fig.set_size_inches(11,8.5)
		# set title
		ax.set_title('Depth to Water')
		# set labels
		ax.set_xlabel('Date')
		ax.set_ylabel('Depth to Water (ft)')

		for well in df['dms_site_id'].unique():
			df_well = df.loc[df['dms_site_id']==well]
			ax.plot(df_well['date'],df_well['meas_depth'])
			ax.scatter(df_well['date'],df_well['meas_depth'],label=well)
		
		ax.legend(
			loc='upper left',
			bbox_to_anchor=(1, 1)
		)

		# rotate x axis labels 45 degrees
		ax.xaxis.set_tick_params(rotation=90,)
		# show every month on x axis
		import matplotlib

		ax.xaxis.set_major_locator(matplotlib.dates.YearLocator(2))
		ax.xaxis.set_minor_locator(matplotlib.dates.YearLocator(1))

		
		# flip y axis
		ax.invert_yaxis()
		ax.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(100))
		ax.yaxis.set_minor_locator(matplotlib.ticker.MultipleLocator(10))

		ax.grid(which='major', axis='both', linestyle='-',linewidth=1)
		ax.grid(which='minor', axis='both', linestyle='--',linewidth=0.5)
		return fig



	def extractions(self):
		fig, ax = plt.subplots()
		# make 8.5x11
		fig.set_size_inches(8.5,11)
		# set title
		ax.set_title('Extractions (AF) by Month')
		# set x axis label
		ax.set_xlabel('Date')
		# set y axis label
		ax.set_ylabel('Extractions (AF)')
		import matplotlib
		# show every month on x axis
		ax.xaxis.set_major_locator(matplotlib.dates.MonthLocator(interval=1))
		# show month name on x axis
		ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%b %Y'))

		
		# rotate x axis labels 45 degrees
		ax.xaxis.set_tick_params(rotation=45,)

		# plt.xticks(rotation=45)

		df = self.data.well_extractions
		df['start_date'] = df.apply(lambda row: arrow.get(row['year'],row['month'],1).datetime, axis=1)


		# well_values = {
		# 	well_id:[e for e in df.loc[df['dms_site_id'] == well_id]['production_af']] for well_id in df['dms_site_id'].unique()
		# }
		# 

		# unique color for each well
		import numpy as np
		colors = plt.cm.tab20c(np.linspace(0, 1, len(df['dms_site_id'].unique()))) 
		well_colors = {well:color for well,color in zip(df['dms_site_id'].unique(),colors)}
		# st.markdown(well_colors)

		# st.markdown(well_values)


		for date in df['start_date'].unique():
			bottom = 0
			days = arrow.get(date).shift(months=1).shift(days=-1).day
			for well in df['dms_site_id'].unique():
				well = df.loc[
					(df['dms_site_id']==well) & (df['start_date']==date)
					].iloc[0]
				# st.dataframe(well)
				# st.markdown(type(days))
				# st.markdown(bottom)

				ax.bar(
					x=well['start_date'],
					height=well['production_af'],
					# label=well['dms_site_id'],
					color=well_colors[well['dms_site_id']],
					width=days,
					bottom=bottom,
					align='edge',
					)
				bottom += well['production_af']
		
		ax.legend(
			[well for well in df['dms_site_id'].unique()],
			loc='upper left',
			bbox_to_anchor=(1, 1)
			)
		
		ax.grid(
			# axis='y',
			which='major',
			linestyle='-',
			linewidth=.5,
			color='black',
		)
		# add minor ticks every 10
		from matplotlib.ticker import MultipleLocator


		ax.yaxis.set_minor_locator(MultipleLocator(10))
		ax.yaxis.set_major_locator(MultipleLocator(50))



		ax.grid(
			# axis='y',
			which='minor',
			linestyle='--',
			linewidth=0.5,
			color='black',
		)

		return fig
	def well_completion(self):
		df = self.data.well_info.drop(columns=['geometry'])
		df['perf_top'] = df['perf_top'].pipe(pd.to_numeric,errors='coerce')
		df['perf_bottom'] = df['perf_bottom'].pipe(pd.to_numeric,errors='coerce')
		df['TotalWell_Depth'] = df['TotalWell_Depth'].dropna().pipe(pd.to_numeric,errors='coerce')

		df = df.dropna(subset=['perf_top','perf_bottom','TotalWell_Depth'])
		with st.expander('Well Completion Data'):
			st.dataframe(df[['dms_site_id','perf_top','perf_bottom','TotalWell_Depth',]],use_container_width=True)

		# st.markdown(df.shape)
		if df.shape[0] == 0:
			st.markdown('No well completion data available')
			return None
		else:
			fig,ax = plt.subplots()
			fig.set_size_inches(h=8.5,w=11)

			# plot well depths
			# df = self.data.well_locations

			# well = df['well_name'].unique()[0]
			# df = df.loc[df['well_name'] == well]


			for well in df['dms_site_id'].unique():
				wdf = df.loc[df['dms_site_id'] == well]
				ax.bar(
					wdf['dms_site_id'],
					wdf['TotalWell_Depth'],
					label=well,
					color='blue',
				)

				ax.bar(
					x=wdf['dms_site_id'],
					bottom=wdf['perf_bottom'],
					height=wdf['perf_top'] - wdf['perf_bottom'],
					color='lightblue',
					hatch='..',
				)


			# rotate x labels
			# x labels up top
			plt.tick_params(axis='x', which='both', bottom=False, top=True, labelbottom=False, labeltop=True,rotation=90)

			# title
			ax.set_title('CVWD Well Depths')

			# y axis title
			ax.set_ylabel('Well Depth (ft)')

			# major y ticks very 25
			ax.set_yticks(range(0,int(df['TotalWell_Depth'].max())+1,50))

			# minor y ticks every 10
			ax.set_yticks(range(0,int(df['TotalWell_Depth'].max())+1,10),minor=True)
			
			ax.grid(axis='y',color='lightgray',linestyle='-',which='major',linewidth=1)
			ax.grid(axis='y',color='lightgray',linestyle='--',which='minor',linewidth=.5)

			# flip y axis
			ax.invert_yaxis()
			return fig


					