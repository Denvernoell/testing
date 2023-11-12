import polars as pl
import plotly.express as px
from pathlib import Path
import matplotlib.pyplot as plt
import streamlit as st


import sys
sys.path.append(r'\\ppeng.com\pzdata\docs\Project Resources\Ag Water\apps\district_management\data')
from sdwis import System, wq_systems
# from districts.cucamonga.data import wq_systems
from districts.cucamonga.wq_config import analyte_groups


def all_systems():
	st.markdown("## SDWIS Water Quality Dashboard")
	st.markdown("### Data Source: [CA Drinking Water Watch](https://sdwis.waterboards.ca.gov/PDWW/JSP/WaterSystemDetail.jsp?tinwsys_is_number=5766&tinwsys_st_code=CA)")
	system_name = st.selectbox("Select a system",wq_systems['Water System Name'].unique())
	row = wq_systems[wq_systems['Water System Name'] == system_name].iloc[0]


	S = System(
		system_number=row['ws_number'],
		is_number=row['is_number'],
	)

	tables = st.selectbox('Select a table', [
		# 'All Data',
		'Single Well',
		# 'Multiple Wells',
		# 'Well Stats'
		])
	if tables == 'All Data':
		c1,c2,c3 = st.columns(3)
		# with st.form(key='my_form'):
				
		with c1:
			ps_code = st.selectbox("Select a well",df['PS Code'].unique())
		with c2:
			# analyte_group = st.selectbox("Select an analyte group",df.filter(pl.col('PS Code') == ps_code)['analyte_group'].unique())
			# convert above line to pandas
			analyte_group = st.selectbox("Select an analyte group",df[df['PS Code'] == ps_code]['analyte_group'].unique())

			
		with c3:
			# analyte_name = st.selectbox("Select an analyte name",df.filter(pl.col('PS Code') == ps_code).filter(pl.col("analyte_group") == analyte_group)['Analyte Name'].unique())
			# convert above line to pandas
			analyte_name = st.selectbox("Select an analyte name",df[df['PS Code'] == ps_code][df['analyte_group'] == analyte_group]['Analyte Name'].unique())

			# submit_button = st.form_submit_button(label='Submit')
			# if submit_button:
		# filtered_df = df.filter(pl.col('PS Code') == ps_code).filter(pl.col("analyte_group") == analyte_group).filter(pl.col("Analyte Name") == analyte_name)
		# convert above line to pandas
		filtered_df = df[df['PS Code'] == ps_code][df['analyte_group'] == analyte_group][df['Analyte Name'] == analyte_name]

				# st.divider()
		st.dataframe(filtered_df,use_container_width=True)
		# st.dataframe(df.to_pandas(),use_container_width=True)
	elif tables == 'Single Well':
		well_id = st.selectbox("Select a well",S.site_urls['Sample Point Name'].unique())
		st.markdown(f"{row['Water System Name']}")
		st.markdown(f"{well_id}")
		wq_data = S.get_wq(well_id)
		import numpy as np
		import pandas as pd

		# st.markdown(analyte_groups)
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

	elif tables == 'Multiple Wells':
		pass
	elif tables == 'Well Stats':
		well_id = st.selectbox("Select a well",df['PS Code'].unique())
		analyte_group = st.selectbox("Select an analyte group",df['analyte_group'].unique())

		def get_well_stats(well):
			return df[df['PS Code'] == well][df['analyte_group'] == analyte_group].groupby(['Analyte Name']).agg({
				'Result':[
					'count',
					'min',
					'max',
					'mean',
					lambda x: x.quantile(0.9)
					]
				}).sort_values(by='Analyte Name')

		
		st.dataframe(get_well_stats(well_id),use_container_width=True)

		# gb = df.groupby('Analyte Name').agg(pl.count('Result').alias('count')).sort('count').to_pandas()#.plot.barh()

def main():
	all_systems()