import json
import pandas as pd
import streamlit as st
from utils.dashboard_shared import Table
from pathlib import Path



def main():
	st.markdown("## Settings")
	st.selectbox(
		"Table",
		[
			'Color',
			# "Wells",
			],
		key="table",
	)
	if st.session_state['table'] == "Color":
			
		table = Table('CB_settings')

		row = table.df.pipe(
			lambda df: df.loc[df['name'] == 'colors'].iloc[0]
		)
		colors = json.loads(row['settings'])
		df = pd.DataFrame(colors,index=["Color"])
		st.dataframe(
			df.style.applymap(lambda x: f"background-color: {x}" if x is not None else "background-color: black")
			)


		c1,c2 = st.columns(2)
		with c1:
			color_row = st.selectbox(
				"select a color",
				colors.keys(),
				)
			if st.button("add color"):
				id = list(colors.keys())[-1]
				new_id = int(id) + 1
				colors[new_id] = '#237b20'
				table.change(
					row=row,
					column='settings',
					new_value=json.dumps(colors),
					index_col='index',
					)
				st.rerun()
		with c2:
			y = colors[color_row]
				
			color = st.color_picker(
					f"edit a color",
					y,
					key=f"color",
					)
			if st.button(
				"change color",
				):
				colors[color_row] = color
				table.change(
					row=row,
					column='settings',
					new_value=json.dumps(colors),
					index_col='index',
					)
				st.rerun()
	elif st.session_state['table'] == "Wells":
		table = Table('CB_well_info')
		data_path = Path(__file__).parent.joinpath('data')
		dfs = pd.read_excel(
			data_path /'well_data_sheet.xlsx',
			sheet_name=None,
		)
		c1,c2,c3 = st.columns(3)
		with c1:
			st.selectbox(
				"select a well",
				table.df['dms_site_id'].unique(),
				key="well",
			)
			row = table.df.pipe(
				lambda df: df.loc[df['dms_site_id'] == st.session_state['well']].iloc[0]
			)
		with c2:
			df = dfs['pivot']
			st.selectbox(
				"select a category",
				df['Well Number or Name'].unique(),
				key="pivot_name",
			)
			pivot_row = df.loc[df['Well Number or Name'] == st.session_state['pivot_name']]
		with c3:
			if st.button("add data"):
				table.change(
					row=row,
					column='WellDataSheet',
					new_value=json.dumps(pivot_json),
					index_col='index',
					)
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
		
		# st.dataframe(pivot_row)
		# pivot_json = pivot_row.to_json()
		# data = json.loads(row['WellDataSheet'])
		# st.markdown(type(data))
		# st.markdown(data)
		# st.dataframe(data)

		# data_json = json.loads(data_dict.read_text())

		# row = table.df.pipe(
		# 	lambda df: df.loc[df['dms_site_id'] == st.session_state['well']].iloc[0]
		# )
		# st.dataframe(row.to_frame().T)



		# from districts.cucamonga.data.well_data_sheet import data_dict
		# data_dict = Path(__file__).parent.joinpath('data','well_data_sheet.json')
		# # data_dict = Path(__file__).parent.joinpath('data','well_data_sheet.json')
		# st.dataframe(pd.DataFrame(data_dict))
		# st.markdown(data_dict)
		# st.markdown(data_dict.read_text())
		# data_json = json.loads(data_dict.read_text())
		# st.markdown(data_json)

		# st.dataframe(
		# 	json.loads(row['WellDataSheet'])
		# )
		# data = json.loads(row['WellDataSheet'])
		# if st.button('cols'):
		# 	df = pd.read_clipboard()#.set_index(0)
		# 	st.dataframe(df)
		# 	opts = [
		# 		'split',
		# 		'records',
		# 		'index',
		# 		'columns',
		# 		'values',
		# 		'table',
		# 		]
		# 	for opt in opts:
		# 		st.markdown(opt)
		# 		try:
		# 			cats = pd.DataFrame(
		# 				Path(__file__).parent.joinpath('data','well_data_sheet.json'),
		# 				orient=opt,
		# 				encoding_errors='ignore',
		# 			)
		# 			st.dataframe(cats)

		# 		except Exception as e:
		# 			st.markdown(e)
					
		# 		J = df.to_json(
		# 			# index=False,
		# 			# indent=2,
		# 			orient=opt,
		# 			indent=5,
		# 			)
		# 		st.markdown(J)
		# 		st.divider()



		# if st.button("clip"):

		# 	df = pd.read_clipboard(header=None)#.set_index(0)
		# 	st.dataframe(df)
		# 	J = df.to_json(
		# 		# index=False,
		# 		# indent=2,
		# 		# orient='split',
		# 		# orient='columns',
		# 		orient='values',
		# 		# orient='records',

		# 		)
		# 	st.markdown(J)


		# if st.button("Add color"):
		# 	st.success("try")
		# 	df = pd.read_clipboard(header=None)#.set_index(0)
		# 	st.dataframe(df)
		# 	J = df.to_json(
		# 		# index=False,
		# 		# indent=2,
		# 		# orient='split',
		# 		# orient='columns',
		# 		orient='values',
		# 		# orient='records',

		# 		)
		# 	st.markdown(J)
		# 	table.change(
		# 		row=row,
		# 		column='WellDataSheet',
		# 		new_value=J,
		# 		index_col='index',
		# 		)
		# 	st.success("Added")
		# 	st.rerun()