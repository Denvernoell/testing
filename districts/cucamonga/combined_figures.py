import matplotlib.pyplot as plt
import arrow
# import matplotlib
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
from matplotlib.ticker import MultipleLocator
import pandas as pd
import streamlit as st

from utils.sdwis import System, wq_systems

class Figure:
	def __init__(self,data):
		self.data = data

class DateFigure(Figure):
	def __init__(self,data,date_range,wells,figures):
		super().__init__(data)
		self.date_range = date_range
		self.wells = wells
		import numpy as np
		self.export_tables = {}


		color_maps = [
			plt.cm.tab20,
			plt.cm.Pastel1,
			plt.cm.tab20c,
		]
		colors = color_maps[0](np.linspace(0, 1, len(wells))) 
		colors = [
				"#ffc080",
				"#80ff80",
				"#c080ff",
				"#f44336",
				"#00bcd4",
				"#4caf50",
				"#9c27b0",
				"#2196f3",
				"#3f51b5",
				"#009688",
				"#673ab7",
				"#e91e63",
				"#ff9800",
				"#795548",
				"#ffff80",
				"#9e9e9e",
				"#80ffc0",
				"#607d8b",
				"#ff8080",
				"#ff80ff",
				"#ff5722",
				"#80ffff",
				"#80c0ff",
				"#ffc107",
				"#ffeb3b",
				"#8080ff",
				"#ff80c0",
			]


		self.well_colors = {well:color for well,color in zip(wells,colors)}

		

		# self.fig = plt.figure(layout='constrained')
		# self.fig.set_size_inches(11,8.5)
		# subfigs = self.fig.subfigures(1, 2, wspace=0.07)

		# if figures == ['DTW',"EBM","WQ","WC"]:
		def try1():
				

			self.fig = plt.figure(
				# layout='constrained',
				)

			# with left and right
			if "Well Completion" not in figures:
				subfig = self.fig.subfigures(1, 1)
			elif figures == ['Well Completion']:
				self.axs2 = self.fig.subfigures(1, 1).subplots(nrows=1,ncols=1)
				self.axs2 = self.well_completion(self.axs2)
				figures.pop(figures.index("Well Completion"))

			else:
				subfigs = self.fig.subfigures(
					1,
					2,
					# increase space between subfigures
					# squeeze=False,
					# wspace=5000,
					width_ratios=[4, 1])
				subfig = subfigs[0]
				self.axs2 = subfigs[1].subplots(
					nrows=1,
					ncols=1,
					# sharex=True,
				)
				self.axs2 = self.well_completion(self.axs2)
				figures.pop(figures.index("Well Completion"))

			
			if len(figures) != 0:
				self.axs = subfig.subplots(
					nrows=len(figures),
					ncols=1,
					sharex=True,
				)
			if len(figures) == 1:
				self.axs = [self.axs]

			
			# self.fig.get_size_inches()
			# l_height = 1.02
			ncol = len(self.wells) if len(self.wells) < 6 else 6
			
			from math import ceil,floor
			nrow = ceil(len(self.wells) / ncol)
			# st.markdown(f"wells: {len(self.wells)}, nrow: {nrow}, ncol: {ncol}")
			l_height = {
				i:1.04 + (i-1)*0.03	for i in range(0,6)
			}
			# add legend on top

			# ncol = 
			self.fig.legend(
				loc='upper center',
				bbox_to_anchor=(0.5, l_height[nrow]),
				ncol=ncol,
				handles=[
					plt.Line2D(
						[0], [0],
						color=self.well_colors[well],
						label=well,
						# linestyle='none',
						marker='o',
						)
					for well in self.wells
				],
				frameon=False,
				# 	'columnspacing':0.5,
				# 	'fontsize':'small',
			)



			# st.markdown(self.fig.get_size_inches())

			i = 0
			if "Depth to Water" in figures:
				self.axs[i] = self.add_depth_to_water(self.axs[i])
				i += 1
			if "Extractions" in figures:
				self.axs[i] = self.add_extractions(self.axs[i])
				i += 1
			if "Water Quality" in figures:
				self.axs[i] = self.add_water_quality(
				# constituent="NITRATE (AS NO3)",
				constituent="NITRATE",
				unit='mg/L',
				ax=self.axs[i],
			)
			# st.markdown(figures)
			if len(figures) != 0:
				years = (date_range[1] - date_range[0]).days / 365
				for ax in self.axs:
					ax.set_xlim(self.date_range[0].date() ,self.date_range[1].date() )
					# st.markdown(days)

					ax.grid(color='gray',which='major', axis='both', linestyle='-',linewidth=1.5)
					ax.grid(color='lightgray',which='minor', axis='both', linestyle='--',linewidth=0.5)


					if years > 10:
						ax.xaxis.set_major_locator(mdates.YearLocator(2))
						ax.xaxis.set_minor_locator(mdates.YearLocator(1))
						ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
					
					elif years < 2:
						ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
						ax.xaxis.set_minor_locator(mdates.DayLocator(15))
						ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
						ax.xaxis.set_tick_params(rotation=90,)
					
					else:
						ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
						ax.xaxis.set_minor_locator(mdates.MonthLocator(interval=1))
						ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
						ax.xaxis.set_tick_params(rotation=90,)
			
			self.fig.set_size_inches(11,8.5)
			
			plt.subplots_adjust(
				# bottom=0.1,
				right=0.85,
				# top=0.9
				)
		try1()




	def add_water_quality(self,constituent,unit,ax):
		# ax.yaxis.set_major_locator(ticker.MultipleLocator(10))
		ax.yaxis.set_minor_locator(ticker.MultipleLocator(1))

		# st.markdown(constituent)
		# df = self.data.well_water_quality

		dfs = []
		for well_id in self.wells:
			well_row = self.data['well_info'].pipe(lambda df:df.loc[df['dms_site_id'] == well_id]).iloc[0]
			
			# if well_row['sdwis_well'] is None:
			# 	st.markdown("No SDWIS well number available")
			# 	# return
			# st.dataframe(well_row)

			if well_row['sdwis_well']:
				row = wq_systems[wq_systems['Water System Name'] == well_row['sdwis_system']].iloc[0]
				S = System(
					system_number=row['ws_number'],
					is_number=row['is_number'],
				)

				wq_data = S.get_wq(
					well_row['sdwis_well'],
					analyte_name=constituent,
					start_date=self.date_range[0],
					)
				
				# TODO figure out how to add data to db and query that first


				# combine into df
				wq_data = wq_data.assign(
					dms_site_id=well_id,
					date=pd.to_datetime(wq_data['Sampling Date']),
					result=pd.to_numeric(wq_data['Results - Detected Level']),
				)
				dfs.append(wq_data)
				# with st.expander(f"{well_id} - {well_row['sdwis_well']}"):
				# 	st.dataframe(wq_data,use_container_width=True)
				# st.success(f"Retrieved water quality data for {well_id}")

		if len(dfs) != 0:
			df = pd.concat(dfs)
		else:
			# st.markdown("No water quality data available")
			df = pd.DataFrame(columns=['dms_site_id','date','result'])
		
		# st.dataframe(df)


		df = df.loc[
			(df['date'] >= self.date_range[0].naive)
			& (df['date'] <= self.date_range[1].naive)
			]
		pivot = df.pivot_table(
			index='date',
			columns='dms_site_id',
			values='result',
			# aggfunc=list,
			aggfunc='mean',
			)
		with st.expander('Water Quality Data'):
			st.dataframe(pivot,use_container_width=True)
			self.export_tables['Water Quality'] = pivot
		

		ax.set_title(f'Water Quality - {constituent}')
		# set labels
		ax.set_ylabel(f'Result ({unit})')

		for well in df['dms_site_id'].unique():
			df_well = df.loc[df['dms_site_id']==well]
			ax.plot(df_well['date'],df_well['result'],color=self.well_colors[well] )
			ax.scatter(df_well['date'],df_well['result'],label=well,color=self.well_colors[well],s=20)
		
		# ax.legend(
		# 	loc='upper left',
		# 	bbox_to_anchor=(1, 1)
		# )
		# st.dataframe(df,use_container_width=True)
		# https://sdwis.waterboards.ca.gov/PDWW/JSP/WSamplingResultsByStoret.jsp?SystemNumber=3610018&SystemName=CUCAMONGA+VALLEY+WATER+DISTRICT&tinwsys_is_number=3782&SamplingPointName=WELL+17&SamplingPointID=027-027-10360&mDWW=null&Analyte=C255&ChemicalName=NITRATE+%28AS+NO3%29&begin_date=&end_date=&Generate+Report=Generate+Report

		return ax



	def add_depth_to_water(self,ax):
		# ax.yaxis.set_major_locator(ticker.MultipleLocator(50))
		ax.yaxis.set_minor_locator(ticker.MultipleLocator(10))
		ax.set_title('Depth to Water')
		ax.set_ylabel('Depth to Water (ft)')


		df = self.data['well_depth_to_water'].pipe(lambda df:df.loc[
			(df['date'] >= self.date_range[0].naive)
			& (df['date'] <= self.date_range[1].naive)
			& (df['dms_site_id'].isin(self.wells))
		])
		depth_col = 'meas_depth'
		pivot = df.pivot_table(
			index='date',
			columns='dms_site_id',
			values=depth_col,
			# aggfunc=list,
			aggfunc='mean',
			)
		with st.expander('Depth to Water Data'):
			st.dataframe(pivot,use_container_width=True)
			self.export_tables['Depth to Water'] = pivot
		self.depth_to_water_df = df
		# set labels
		# ax.set_xlabel('Date')

		for well in df['dms_site_id'].unique():
			df_well = df.loc[df['dms_site_id']==well]
			ax.plot(df_well['date'],df_well[depth_col],color=self.well_colors[well])
			ax.scatter(df_well['date'],df_well[depth_col],label=well,color=self.well_colors[well],s=20)
		
		# y bounds
		# ax.set_ylim(
		# 	# 0,
		# 	df[depth_col].min()-10,
		# 	df[depth_col].max()+10,
		# 	)
		
		# ax.legend(
		# 	loc='upper left',
		# 	bbox_to_anchor=(1, 1)
		# )

		# flip y axis
		ax.invert_yaxis()
		return ax



	def add_extractions(self,ax):
		df = self.data['well_extractions']
		# st.dataframe(df)
		extraction_col = 'production_af'

		ax.set_ylabel('Volume Extracted (AF)')
		# df[extraction_col].max()

		# st.dataframe(df)
		df['start_date'] = df.apply(lambda row: arrow.get(row['date']).date(), axis=1)

		pivot = df.pivot_table(
			index='date',
			columns='dms_site_id',
			values=extraction_col,
			aggfunc='mean',
			# aggfunc=list,
			)
		with st.expander('Extraction Data'):
			st.dataframe(pivot,use_container_width=True)
			self.export_tables['Extractions'] = pivot

		for date in df['start_date'].unique():
			bottom = 0

			days = arrow.get(date).shift(months=1).shift(days=-1).day
			for well in df['dms_site_id'].unique():
				try:
						
					well = df.loc[
						(df['dms_site_id']==well) & (df['start_date']==date)
						].iloc[0]

					ax.bar(
						x=well['start_date'],
						height=well[extraction_col],
						# label=well['dms_site_id'],
						color=self.well_colors[well['dms_site_id']],
						width=days,
						bottom=bottom,
						align='edge',
						)
					bottom += well[extraction_col]
				except:
					pass
		# if st.checkbox('Show Rainfall Data'):
		if st.session_state['show_rainfall']:
			ax.set_title('Extractions and Rainfall by Month')
			# add rainfall
			import sys
			from pathlib import Path
			# data_path = r'\\ppeng.com\pzdata\docs\Project Resources\Ag Water\apps\district_management\data'

			# sys.path.append(data_path)
			from utils.CDEC import CDEC

			DYC = CDEC('DYC',date_range=self.date_range)
			rain_df = DYC.get_data(
				45,"D"
			)
			month_rain_df = rain_df.groupby([
				rain_df.index.year,rain_df.index.month
			]).sum()
			month_rain_df.index = pd.to_datetime(
				month_rain_df.index.to_series().apply(lambda x: f'{x[0]}-{x[1]}')
				)
			
			ax2 = ax.twinx()
			ax2.bar(
				month_rain_df.index,
				month_rain_df['value'],
				label='Rainfall',
				color='#C4DDFF',
				alpha=.6,
				width=31,
				align='edge',
				hatch='.',
				)
			ax2.set_ylabel('CDEC DYC Rainfall (in)')
			# ax2.set_ylim(0,ax2.get_ylim()[1]*2)
			ax2.set_ylim(0,25)
			
			# flip y axis
			ax2.invert_yaxis()
			ax.set_ylim(0,ax.get_ylim()[1]*1.3)
		else:
			ax.set_title('Extractions by Month')

		
		# ax.legend(
		# 	[well for well in df['dms_site_id'].unique()],
		# 	loc='upper left',
		# 	bbox_to_anchor=(1, 1)
		# 	)
		
		# st.markdown(ax.get_ylim())
		if ax.get_ylim()[1] < 200:
			ax.yaxis.set_minor_locator(MultipleLocator(5))
			ax.yaxis.set_major_locator(MultipleLocator(20))
		else:	
			ax.yaxis.set_minor_locator(MultipleLocator(25))
			ax.yaxis.set_major_locator(MultipleLocator(100))
		# ax.yaxis.set_major_locator(MultipleLocator(50))
		return ax
	
	def well_completion(self,ax):
		df = self.data['well_info'].drop(columns=['geometry'])
		df['perf_top'] = df['perf_top'].pipe(pd.to_numeric,errors='coerce')
		df['perf_bottom'] = df['perf_bottom'].pipe(pd.to_numeric,errors='coerce')
		df['TotalWell_Depth'] = df['TotalWell_Depth'].dropna().pipe(pd.to_numeric,errors='coerce')

		depth_col = 'meas_depth'


		df = df.dropna(subset=['perf_top','perf_bottom','TotalWell_Depth'])
		# with st.expander('Well Completion Data'):
		# 	st.dataframe(df[['dms_site_id','perf_top','perf_bottom','TotalWell_Depth',]],use_container_width=True)

		# st.markdown(df.shape)
		if df.shape[0] == 0:
			# st.markdown('No well completion data available')
			df = pd.DataFrame(columns=['dms_site_id','perf_top','perf_bottom','TotalWell_Depth',])
			
		else:
			for well in self.wells:
				wdf = df.loc[df['dms_site_id'] == well]
				# add min and max depth to water in range
				
				# ax.axhline(
				# 	y=row['min_depth_to_water'],
				# 	# xmin=row['dms_site_id'],
				# 	# xmax=row['dms_site_id'],
				# 	color='green',
				# )
				# ax.axhline(
				# 	y=row['max_depth_to_water'],
				# 	# xmin=0,
				# 	# xmax=0,
				# 	color='red',
				# )

				ax.bar(
					wdf['dms_site_id'],
					wdf['TotalWell_Depth'],
					label=well,
					color=self.well_colors[well],
				)

				ax.bar(
					x=wdf['dms_site_id'],
					bottom=wdf['perf_bottom'],
					height=wdf['perf_top'] - wdf['perf_bottom'],
					color=self.well_colors[well],
					hatch='..',
				)
				# depth to water
				try:
						
					dtw_df = self.data['well_depth_to_water'].pipe(lambda df:df.loc[
						(df['date'] >= self.date_range[0].naive)
						& (df['date'] <= self.date_range[1].naive)
						& (df['dms_site_id'] == well)
					])
					# st.dataframe(df)
					# if self.depth_to_water_df:
					wdf['min_depth_to_water'] = dtw_df[depth_col].min()
					wdf['max_depth_to_water'] = dtw_df[depth_col].max()
					# st.dataframe(wdf)
					row = wdf.iloc[0]
					ax.bar(
						x=wdf['dms_site_id'],
						bottom=wdf['max_depth_to_water'],
						height=wdf['min_depth_to_water'] - wdf['max_depth_to_water'],
						color='#C4DDFF',
						hatch='O.',
					)
				except:
					pass

			# major y ticks very 25
			ax.set_yticks(range(0,int(df['TotalWell_Depth'].max())+1,50))

			# minor y ticks every 10
			ax.set_yticks(range(0,int(df['TotalWell_Depth'].max())+1,10),minor=True)
		# title
		ax.set_title('Well Construction')
		

		# ticks and labels on right
		ax.yaxis.tick_right()

		# label on right

		ax.set_ylabel('Well Depth (ft)')
		ax.yaxis.set_label_position("right")



		# remove x ticks
		ax.set_xticks([])			

		# flip y axis
		ax.invert_yaxis()


		# add box about dotted being perforation interval
		date_range = self.date_range
		ax.text(
		0.5, .99, 'Dotted: Perforation Interval\nBlue Circles: DTW Range for\n' + date_range[0].format('MM/DD/YYYY') + ' - ' + date_range[1].format('MM/DD/YYYY'),
			transform=ax.transAxes,
			ha='center',
			va='top',
			bbox=dict(boxstyle='round', facecolor='white', alpha=0.9)
			)

		return ax
	def map_boundaries(self,ax):
		
		return ax
