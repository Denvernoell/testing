import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import arrow

from utils.dashboard_shared import download_pdf
# from districts.general.figures import Map
import leafmap.foliumap as leafmap

from utils.sdwis import System, wq_systems
from districts.cucamonga.wq_config import analyte_groups

from districts.cucamonga.general import Data,Wells,Agency

from districts.cucamonga.figures import Figure
from utils.figures import Map

from districts.cucamonga.combined_figures import DateFigure

from districts.cucamonga.data import data

# @st.cache_data
# def get_data():
# 	return Data()

# @st.cache_data
# def get_wells(wells):
# 	return Wells(wells)

# @st.cache_data
# def get_agency(agency):
# 	if agency == "P&P":
# 		return Data()
# 	else:
# 		return Agency(agency)

def main():
	# data = get_data()

	# if st.button("Refresh"):
	# 	st.rerun()

	# M = leafmap.Map()
	M = Map()
	all_wells = data.well_info.sort_values(by='dms_site_id')

	c1,c2,c3,c4,c5 = st.columns(5)
	with c1:
		st.selectbox('Selection type',[
			'Wells',
			"Group",
			'Agency',
		],key='selection_type')
		
		if st.session_state['selection_type'] == 'Wells':
			st.multiselect(
				'Agencies',
				data.well_info['Monitor_By'].unique(),
				default=data.well_info['Monitor_By'].unique(),
				key='filters')
			# well_subset = data.well_info.loc[~data.well_info['Monitor_By'].isin(st.session_state['filters'])]

	with c2:
		if st.session_state['selection_type'] == 'Wells':
			if st.session_state['filters']:
				well_subset = data.well_info.loc[data.well_info['Monitor_By'].isin(st.session_state['filters'])]
			else:
				well_subset = data.well_info
			# well_subset = data.well_info.loc[data.well_info['Monitor_By'].isin(st.session_state['filters'])]

			st.multiselect('Select Wells',well_subset['dms_site_id'],default=[],key='wells')

		elif st.session_state['selection_type'] == 'Agency':
			groups = {			
				agency:data.well_info.loc[data.well_info['Monitor_By'] == agency]['dms_site_id'].unique()
				for agency in data.well_info['Monitor_By'].unique()
			}
			st.selectbox('Select a group',list(groups.keys()),key='group')
			st.session_state['wells'] =  groups[st.session_state['group']]
			
		elif st.session_state['selection_type'] == 'Group':
			groups = {
				"CVWD 1":['CVWD 17','CVWD 19','CVWD 24'],
				"SAWCo 1":['SAWC 12', 'SAWC 15'],
			}
			st.selectbox('Select a group',list(groups.keys()),key='group')
			st.session_state['wells'] =  groups[st.session_state['group']]
	
	# st.markdown("## Data")
	# st.markdown(data)
	# st.markdown(st.session_state['wells'])
	well_data = data.filter_wells(st.session_state['wells'])
	# st.markdown(well_data)
	# st.dataframe(well_data.well_info.drop(columns='geometry'),use_container_width=True)

	with c3:	
		st.selectbox('Select an output',[
		'Combined',
		# 'Map',
		'Heatmap',
		# 'Hydrograph',
		# 'Extractions',
		# 'Well Completion',
		# "SDWIS Water Quality",
		# 'Water Quality',
		]
		,key='output')
	
	if st.session_state['output'] == 'Heatmap':
		st.markdown("## Heatmap")

# https://stackoverflow.com/questions/59181855/get-the-financial-year-from-a-date-in-a-pandas-dataframe-and-add-as-new-column		
		c1,c2,c3 = st.columns(3)
		period_types = [
			'Fiscal Year',
			'Water Year',
			'Calendar Year',
			'Monthly',
			"Quarterly",
		]
		with c1:
			st.selectbox(
				"Time Period",
				# time_periods.keys(),
				period_types,
				key='period_type')

		with c2:
			st.selectbox("Metric",[
				'Extractions',
				'Depth to Water',
				# 'Water Quality'
				],key='metric')
		
		if st.session_state['metric'] == 'Extractions':
			df = well_data['well_extractions']
			value_name = "production_af"
			agg = 'sum'
			units = 'AF'
		if st.session_state['metric'] == 'Water Quality':
			df = well_data['well_extractions']
			value_name = "production_af"
			agg = 'mean'
			units = "mg/L"
		if st.session_state['metric'] == 'Depth to Water':
			df = well_data['well_depth_to_water']
			value_name = "meas_depth"
			agg = 'mean'
			units = "ft"
		
		# st.dataframe(df)
		df['date'] = df['date'].astype('datetime64[ns]')
		df['water_year'] = df['date'].map(lambda x: x.year if x.month > 10 else x.year-1)
		df['fiscal_year'] = df['date'].map(lambda x: x.year if x.month > 7 else x.year-1)


			
		time_periods = {
			'Fiscal Year':df['fiscal_year'],
			'Water Year':df['water_year'],
			'Calendar Year':df.date.dt.year,
			'Monthly':df.date.dt.month,
			"Quarterly":df.date.dt.quarter,
			# "Q1":[1,2,3],
			# "Q2":[4,5,6],
			# "Q3":[7,8,9],
			# "Q4":[10,11,12],
		}
		# df.date.dt.year,
		# st.dataframe(df)

		gb = df.groupby([
			'dms_site_id',
			time_periods[st.session_state['period_type']]],
		).agg({value_name:agg}).reset_index().rename(columns={
			value_name:'value',
			'fiscal_year':'date',
			'water_year':'date',
			})
		
		# st.dataframe(gb)
		with c3:
			st.selectbox("Time",gb['date'].unique(),key='period_selection')

		df = gb.pipe(lambda df: df.loc[
			df['date'] == st.session_state['period_selection']
			])
		with st.expander('Data'):
			st.dataframe(df,use_container_width=True)
	
		df = pd.merge(df,well_data['well_info'].drop(columns=['geometry']),on='dms_site_id')
		all_boundaries = data.boundaries['name'].unique()
		# boundaries = st.multiselect('Select a boundary',all_boundaries,default=all_boundaries)

		def add_leaflet_map():
				
			M.add_boundaries(boundary)

			M.map.add_heatmap(
				data=df,
				latitude='Latitude',
				longitude='Longitude',
				value='value',
				radius=20,
				# blur=10,
				name='Heatmap',
				# radius=50,
				# gradient={0.1: '#FFF3E2', 0.4: '#FFE5CA', 0.6: '#FFABAB', 0.8: '#FA9884', 1.0: '#E74646'},
			)
			# for i,y in df.iterrows():
			df['label'] = df.apply(lambda x: f"<b>{x['dms_site_id']}</b><br>{x['value']:,.2f} {units}",axis=1)
			M.map.add_circle_markers_from_xy(
				df,
				x='Longitude',
				y='Latitude',
				radius=5,
				fill_opacity=0.4,
				tooltip='label',
				fill_color='blue',
				)
		

			M.map.to_streamlit()
		# add_leaflet_map()	
		import pydeck as pdk
		# ddf = [['value','Latitude','Longitude']]

		# st.dataframe(boundary.drop(columns='geometry'),)
		# bdy = boundary#.iloc[0]['geometry']
		# st.markdown(bdy)
		
		if st.session_state['metric'] == 'Extractions':
			df['label_value'] = df['value'].apply(lambda x: f"Volume Extracted: {x:,.0f} AF")
		# if st.session_state['metric'] == 'Water Quality':
		if st.session_state['metric'] == 'Depth to Water':
			df['label_value'] = df['value'].apply(lambda x: f"Average Depth to Water: {x:,.2f} ft")

		map_styles = {
			'Satellite':pdk.map_styles.SATELLITE,
			'Road':pdk.map_styles.MAPBOX_ROAD,
			'Light':pdk.map_styles.MAPBOX_LIGHT,
			'Dark':pdk.map_styles.DARK,
			"Carto":pdk.map_styles.CARTO_ROAD,
		}
		c1,c2,c3 = st.columns(3)
		with c1:
			st.selectbox('Select a boundary',all_boundaries,key='boundary')
			boundary = data.boundaries.loc[data.boundaries['name'] == st.session_state['boundary']]
			bdy = boundary
		with c2:
			st.selectbox('Select a map style',map_styles.keys(),key='map_style')
		with c3:
			st.button('Create Map',key='create_map',help='This may take a minute',use_container_width=True)
		def add_3d():
			from pydeck.types import String

			st.pydeck_chart(pdk.Deck(
				# map_style=None,
				map_style=map_styles[st.session_state['map_style']],
				# map_style='satellite',
				initial_view_state=pdk.ViewState(
					latitude=bdy.geometry.centroid.y.iloc[0],
					longitude=bdy.geometry.centroid.x.iloc[0],
					zoom=12,
					pitch=70,
				),
				map_provider='mapbox',
				api_keys={'mapbox':st.secrets['mapbox']['token']},
				tooltip={
					# "html": "<b>{mrt_distance}</b> meters away from an MRT station, costs <b>{price_per_unit_area}</b> NTD/sqm",
					"html": "<b>{dms_site_id}</b><br>{label_value}",
					"style": {"backgroundColor": "steelblue", "color": "white"},
				},
				layers=[

					pdk.Layer(
						# 'PolygonLayer',
						'GeoJsonLayer',
						data=bdy,
						# get_polygon="-",
						get_fill_color=[
							145,
							200,
							228,
						],
						# get_position='[Longitude, Latitude]',
						opacity=0.2,
						# stroked=True,
						# wireframe=True,
						# get_elevation=['value'],
						# extruded=True,
						# get_color='[200, 30, 0, 160]',
						# get_radius=200,
					),
					pdk.Layer(
						'ColumnLayer',
						# data=df.fillna(value={'value':0}),
						data=df.fillna(0),
						get_position='[Longitude, Latitude]',
						get_elevation='value',
						radius=20,
						get_color='[12,129,246]',
						
						pickable=True,
						auto_highlight=True,
						# elevation_scale=4,
						opacity=0.6,
						# # stroked=True,
						# # wireframe=True,
					),
					pdk.Layer(
						'HeatmapLayer',
						data=df.fillna(0),
						get_position='[Longitude, Latitude]',
						aggregation=String('MEAN'),
						get_weight='value',
						# radius=20,
						# get_color='[12,129,246]',
						
						# pickable=True,
						# auto_highlight=True,
						# # elevation_scale=4,
						# opacity=0.6,
						# # # stroked=True,
						# # # wireframe=True,
					),
				],
			))
		if st.session_state['create_map']:

			try:
				add_3d()
			except Exception as e:
				st.error(e)
				# st.rerun()
				# add_3d()
			# st.markdown("## Figures")

	if st.session_state['output'] == 'Combined':
		# c1,c2 = st.columns(2)
		from datetime import date

		# with c4:
		# 	st.date_input(
		# 		'Date Range',
		# 		# value=date(2018,1,1),
		# 		value=(date(2018,10,1),date(2022,10,1)),
		# 		key='date_range'
		# 		)
		# 	# date_range=st.session_state['date_range']
		# 	date_range = [
		# 	arrow.get(st.session_state['date_range'][0]),
		# 	arrow.get(st.session_state['date_range'][1]),
		# ]
		figs = [
			"Depth to Water",
			"Extractions",
			"Water Quality",
			"Well Completion",
		]
		
		with c4:
			st.date_input(
				'Start date',
				# value=date(2018,1,1),
				value=date(2018,10,1),
				key='start_date'
				)
		with c5:
			# st.date_input('End date',value=date.today(),key='end_date')
			st.date_input(
				'End date',
				# value=date(2022,9,1),
				value=date(2022,10,1),
				key='end_date'
				)
		date_range = [
			arrow.get(st.session_state['start_date']),
			arrow.get(st.session_state['end_date']),
		]
		c1,c2 = st.columns(2)
		with c1:
			st.multiselect("Figures",options=figs,default=figs,key='figs')
		# with c2:
			st.checkbox('Show Rainfall Data',key='show_rainfall')
		with c2:
			st.button('Get data',key='get_data',use_container_width=True)
		if st.session_state['get_data']:
		# if st.button('Create Figures',key='create_figs'):
			F = DateFigure(well_data,date_range,wells=st.session_state['wells'],figures=st.session_state['figs'])

			fig = F.fig
			fig.tight_layout()
			st.pyplot(fig,use_container_width=True)
			fig_name = 'Combined'
		# fig.savefig(f'{fig_name}.pdf')
		# download_pdf(
		# 	# fig,
		# 	f'{fig_name}.pdf',
		# 	f'{fig_name}',
		# 	f'{fig_name}',
		# )

		# if st.button('Export Tables'):
			# https://stackoverflow.com/questions/67564627/how-to-download-excel-file-in-python-and-streamlit
			# create excel workbook from F.export_tables
			table_names = {
				"Depth to Water":"Depth to Water (ft)",
				"Extractions":"Extractions by Month (AF)",
				"Water Quality":"Nitrate concentration (mg_L)",
				"Well Completion":"Well Construction",
			}
			import io
			import base64
			output = io.BytesIO()
			writer = pd.ExcelWriter(
				output,
				engine='xlsxwriter',
				datetime_format='yyyy-mm-dd',
				date_format='yyyy-mm-dd',
				options={'auto_width': True},
				# auto_width=True,
				)
			for k,v in F.export_tables.items():
				# st.markdown(k)
				v.to_excel(writer, sheet_name=table_names[k])
				# st.dataframe(v)
			workbook = writer.book

			# ymd = workbook.add_format({'num_format': 'yyyy-mm-dd'})

			# format_changes = {
			# 	"Depth to Water":{"A":ymd},
			# }
			# for k,v in format_changes.items():
			# 	worksheet = writer.sheets[k]
			# 	for col,format in v.items():
			# 		worksheet.set_column(f'{col}:{col}', None, format)

			writer.save()
			
			# st.markdown(type(towrite))
			st.download_button(
				label="Download Excel File",
				data=output,
				file_name="cb_well_export.xlsx",
				# mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
			)
			# st.markdown(type(writer))
			# file_name = f'cb_well_export'
			# towrite.seek(0)  # reset pointer
			# b64 = base64.b64encode(towrite.read()).decode()  # some strings
			# linko= f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{file_name}">Download excel file</a>'
			# st.markdown(linko, unsafe_allow_html=True)on('Create Figures',key='create_figs')



	if st.session_state['output'] == 'Map':
		well_gdf = all_wells.loc[all_wells['dms_site_id'].isin(st.session_state['wells'])]

		M.add_markers_and_labels(
			well_gdf,
			label_col='dms_site_id',
			color='blue',
			icon='glyphicon glyphicon-tint',
			hover_cols=['dms_site_id','LocalSite_ID','Monitor_By','WellUse','WellStatus',],
			# popup_cols=['dms_site_id','LocalSite_ID','Monitor_By','WellUse','WellStatus',],
			name='Wells',
			)

		all_boundaries = data.boundaries['name'].unique()
		# boundaries = st.multiselect('Select a boundary',all_boundaries,default=all_boundaries)
		boundaries = st.selectbox('Select a boundary',all_boundaries)
		boundary_gdf = data.boundaries.loc[data.boundaries['name'].isin([boundaries])]
		M.add_boundaries(boundary_gdf)
		M.map.to_streamlit()

		with st.expander('Raw Data'):
			st.dataframe(all_wells.drop(columns='geometry'),use_container_width=True)

	if st.session_state['output'] == "SDWIS Water Quality":
		st.markdown("## SDWIS Water Quality Dashboard")
		# st.markdown(well_data)
		wq_rows = well_data['well_info'].dropna(
			subset=['sdwis_well']
		)
		well_id = st.selectbox("Select a well",wq_rows['dms_site_id'].unique())
		well_row = wq_rows.loc[wq_rows['dms_site_id'] == well_id].iloc[0]

		
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
				analyte_name="NITRATE (AS NO3)"
				)
			# if wq_data is not None:
			
			st.dataframe(wq_data,use_container_width=True)

			import numpy as np

			# invert dictionary
			analyte_group_map = {v: k for k, vs in analyte_groups.items() for v in vs}


			wq_data['analyte_group'] = wq_data['Analyte Name'].apply(lambda x: analyte_group_map.get(x))
			wq_data['analyte_group'] = wq_data['analyte_group'].fillna(value='Not Classified')

			summary_df = wq_data.fillna(value={"Results - Detected Level":0}).groupby(["analyte_group",'Analyte Name',"Unit"]).agg({
				'Results - Detected Level':[len,min,'mean',max,lambda x: np.percentile(x,90)],
			}).rename(columns={
				'len':'Data Points Available',
				'min':'Min',
				'mean':"Average",
				'max':'Max',
				'<lambda_0>':'90th Percentile'
				})['Results - Detected Level'].sort_values(by=['analyte_group','Analyte Name'])


			st.dataframe(
				summary_df,
				# wq_data,
				use_container_width=True)

	if st.session_state['output'] == "Water Quality":
		total_df = well_data['well_water_quality']
		constituent = st.selectbox('Select a constituent',total_df['constituent'].unique())
		df = total_df.loc[total_df['constituent'] == constituent]
		time_period = st.selectbox('Select a time period',[
			'Yearly',
			'Monthly',
			'Daily',
			])
		if time_period == 'Yearly':
			f_df= df
			gb_cols = [df.date.dt.year]
			column_config = {'date':st.column_config.TextColumn(label="Year") }
		elif time_period == 'Monthly':
			year = st.selectbox('Select a year',df.date.dt.year.unique())
			f_df = df.loc[df.date.dt.year == year]
			gb_cols = [df.date.dt.month]
			column_config = {'date':st.column_config.TextColumn(label="Month")}
		elif time_period == 'Daily':
			year = st.selectbox('Select a year',df.date.dt.year.unique())
			f_df = df.loc[df.date.dt.year == year]
			gb_cols = [df.date.dt.date]
			column_config = {'date':st.column_config.DateColumn(label="Date",format="M/D/YYYY") }

		# summary table
		summary = f_df.groupby(['constituent'] + gb_cols).agg(
			['mean','min','max','std','count']
			)['result'].round(2)
		summary.columns = ['mean','min','max','std','count']
		summary = summary.reset_index().drop(columns='constituent')
		# summary['date'] = summary.apply(lambda x: arrow.get(f'{x.year}-{x.month}-01').format('MMM YYYY'),axis=1)
		# summary['date'] = summary.apply(lambda x: arrow.get(f'{x.year}-{x.month}-01').format('MMM YYYY'),axis=1)
		st.dataframe(
			summary,
			column_config=column_config,
			hide_index=True,
			use_container_width=True,
			)


		max_date,min_date = df['date'].max(),df['date'].min()
		# well_data
		c1,c2 = st.columns(2)
		with c1:
			start_date = st.date_input('Start date',value=min_date)
		with c2:
			end_date = st.date_input('End date',value=max_date)
		# st.markdown(type(start_date))


		# st.dataframe(df)
		F = Figure(well_data)
		fig = F.mpl_water_quality(
			constituent=constituent,
			unit="",
			start_date=start_date,
			end_date=end_date)
		fig.tight_layout()
		st.pyplot(fig)
		fig_name = 'Water Quality'
		fig.savefig(f'{fig_name}.pdf')
		download_pdf(
			# fig,
			f'{fig_name}.pdf',
			f'{fig_name}',
			f'{fig_name}',
		)



	if st.session_state['output'] == 'Hydrograph':
		df = well_data['well_depth_to_water']
		max_date,min_date = df['date'].max(),df['date'].min()

		# well_data
		c1,c2 = st.columns(2)
		with c1:
			start_date = st.date_input('Start date',value=min_date)
		with c2:
			end_date = st.date_input('End date',value=max_date)
		# st.markdown(type(start_date))

		# st.dataframe(df)


		F = Figure(well_data)
		fig = F.mpl_depth_to_water(start_date=start_date,end_date=end_date)
		fig.tight_layout()
		st.pyplot(fig)
		fig_name = 'Depth to Water'
		fig.savefig(f'{fig_name}.pdf')
		download_pdf(
			# fig,
			f'{fig_name}.pdf',
			f'{fig_name}',
			f'{fig_name}',
		)
	if st.session_state['output'] == 'Extractions':
			

		F = Figure(well_data)
		fig = F.extractions()
		if fig is not None:
			fig.tight_layout()
			st.pyplot(fig)
		# if st.button('Export PDF'):
		fig.savefig('extractions.pdf')
		download_pdf(
			# fig,
			'extractions.pdf',
			'extractions',
			'extractions',
		)
	if st.session_state['output'] == 'Well Completion':
		F = Figure(well_data)
		fig = F.well_completion()
		if fig is not None:
			fig.tight_layout()
			st.pyplot(fig)
			# if st.button('Export PDF'):
			fig_name = 'Well Completion'
			fig.savefig(f'{fig_name}.pdf')
			download_pdf(
				# fig,
				f'{fig_name}.pdf',
				f'{fig_name}',
				f'{fig_name}',
			)



