import streamlit as st
import plotly.graph_objects as go
import pandas as pd

import arrow

from testing.utils.dashboard_shared import Table, GIS_REST, servers
from districts.general.figures import Map


from districts.cucamonga.general import Data
from districts.cucamonga.figures import Map,Figure

def main():
	data = Data()
	# st.dataframe(Table('CB_well_info').df,use_container_width=True)
	# st.dataframe(Table('CB_gis_boundaries').df,use_container_width=True)
	M = Map()

	all_wells = Table('CB_well_info').df
	all_agencies = all_wells['Monitor_By'].unique()

	agencies = st.multiselect('Select an agency',all_agencies,default=all_agencies)

	
	wells_in_agencies = all_wells.loc[all_wells['Monitor_By'].isin(agencies)]['dms_site_id'].unique()

	wells = st.multiselect('Select a well',wells_in_agencies,default=wells_in_agencies)

	M.add_wells(wells)

	all_boundaries = data.boundaries['name'].unique()
	# boundaries = st.multiselect('Select a boundary',all_boundaries,default=all_boundaries)
	boundaries = st.selectbox('Select a boundary',all_boundaries)
	M.add_boundaries([boundaries])
	M.map.to_streamlit()

	water_levels = Table('CB_well_water_levels').df.pipe(lambda df: df.loc[df['dms_site_id'].isin(wells)]).sort_values('meas_date')
	# st.dataframe(all_wells,use_container_width=True)

	# st.write(data.boundaries)
	F = Figure()
	F.depth_to_water(water_levels)
	st.plotly_chart(F.fig,use_container_width=True)
	with st.expander('Raw Data'):
		st.dataframe(all_wells,use_container_width=True)