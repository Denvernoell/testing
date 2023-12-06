import streamlit as st
import plotly.graph_objects as go
import pandas as pd

import arrow

from testing.utils.dashboard_shared import Table, GIS_REST, servers,download_pdf
from districts.general.figures import Map


from districts.cucamonga.general import Data,Wells
from districts.cucamonga.figures import Figure

@st.cache_data
def get_data():
	return Data()

@st.cache_data
def get_wells(wells):
	return Wells(wells)

def main():
	data = get_data()
	# st.dataframe(Table('CB_well_info').df,use_container_width=True)
	# st.dataframe(Table('CB_gis_boundaries').df,use_container_width=True)
	M = Map()

	all_wells = data.well_info
	# st.dataframe(all_wells.drop(columns=['geometry']))

	all_agencies = all_wells['Monitor_By'].unique()

	agencies = st.multiselect('Select Agencies',all_agencies,default=all_agencies)

	
	wells_in_agencies = all_wells.loc[all_wells['Monitor_By'].isin(agencies)]['dms_site_id'].unique()

	wells = st.multiselect('Select Wells',wells_in_agencies,default=wells_in_agencies)

	output = st.selectbox('Select an output',('Map','Hydrograph','Extractions','Well Completion'))
	well_data = get_wells(wells)
	if output == 'Map':
		well_gdf = all_wells.loc[all_wells['dms_site_id'].isin(wells)]

		M.add_markers_and_labels(
			well_gdf,
			label_col='dms_site_id',
			color='blue',
			icon='glyphicon glyphicon-tint',
			hover_cols=['dms_site_id','LocalSite_ID','Monitor_By','WellUse','WellStatus',],
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
	# water_levels = Table('CB_well_water_levels').df.pipe(lambda df: df.loc[df['dms_site_id'].isin(wells)]).sort_values('meas_date')
	# # st.dataframe(all_wells,use_container_width=True)

	# # st.write(data.boundaries)
	# F = Figure(data)
	# F.depth_to_water(water_levels)
	# st.plotly_chart(F.fig,use_container_width=True)
	if output == 'Hydrograph':
			
		df = well_data.well_depth_to_water
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
	if output == 'Extractions':
			

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
	if output == 'Well Completion':
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
