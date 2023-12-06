import streamlit as st
from utils.dashboard_shared import Table
from pathlib import Path
import pandas as pd
import json

def main():

	name_table = Table('CB_well_names').df.dropna(subset=['name_wds']).sort_values('dms_site_id')
	table = Table('CB_well_info')
	data_path = Path(__file__).parent.joinpath('data')
	dfs = pd.read_excel(
		data_path /'well_data_sheet.xlsx',
		sheet_name=None,
	)

	df = dfs['pivot']
	# st.markdown(df['Well Number or Name'].unique())
	# st.markdown(name_table['name_wds'].unique())
	names =name_table['name_wds'].unique()
	st.selectbox(
		"select a category",
		names,
		# df['Well Number or Name'].unique(),

		key="pivot_name",
	)
	pivot_row = df.loc[df['Well Number or Name'] == st.session_state['pivot_name']]
	file_path = str(data_path / "categories.json")
	with open(file_path, 'r') as j:
		categories = json.loads(j.read())
	# st.markdown(categories)
	for category in categories:
		st.markdown(f"## {category}")

		cat_df = pivot_row[categories[category]].T
		cat_df.columns = ['value']
		# cat_df.index.name = category
		cat_df.index.name = "Name"
		# cat_df_styled = cat_df.style.applymap(lambda x: f"color: transparent" if x is not None else "color: black")
		cat_df_styled = cat_df#.style.highlight_null(props='color:transparent;')
		# st.dataframe(cat_df_styled,use_container_width=True)
		st.data_editor(cat_df_styled,use_container_width=True)