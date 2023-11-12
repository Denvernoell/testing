import streamlit as st
import pandas as pd

from utils.dashboard_shared import Table
import arrow


def show_edits(entry_table):
	txt = f"Proposed changes\n\n------------------"
	for row_num,data in st.session_state['entry_table']['edited_rows'].items():
		row = entry_table.iloc[row_num].name
		txt += f"\n\n{row}:"
		for col,change in data.items():
			txt += f" {col} -> {change};"
	st.info(txt)

def main():
	st.markdown("## Data Input")
	tables = {
		"Well Production":'CB_well_production_monthly_af',
		"Well Info":'CB_well_info',
		"Well Water Levels":'CB_well_water_levels',
		"Well Names":'CB_well_names',
		# "Water Quality":"CB_well_water_quality",
		"CVWD Production":'CB_well_production_monthly_af',
	}
	table_name = st.selectbox('Select a table',list(tables.keys()))
	table = Table(tables[table_name])

	agency_names = {
		"Cucamonga Valley Water District":"CVWD",
		"San Antonio Water Company":"SAWCo",
		"West End Consolidated Water Company":'WEWC',
	}
	if table_name == 'CVWD Production':
		
		name_list = ["Well 1","Well 4","Well 5","Well 8","Well 10","Well 12","Well 13","Well 15","Well 16","Well 17","Well 19","Well 20","Well 21","Well 22","Well 23","Well 24","Well 26","Well 30","Well 31","Well 33","Well 34","Well 38"]
		# replace "CVWD 01" with "Well 1" for cvwd_list with zfill 2
		name_table = Table('CB_well_names').df.pipe(lambda df:df.loc[df['name_production'].isin(name_list)])
		name_map = {y['dms_site_id']:y['name_production'] for x,y in name_table.iterrows()}
		r_name_map = {y['name_production']:y['dms_site_id'] for x,y in name_table.iterrows()}

		# cvwd_list = [name_map[x] for x in name_list]
		entry_table = table.df.pipe(lambda df:df.loc[df['dms_site_id'].isin(name_map.keys())]).sort_values('date')
		# entry_table = table.df
		pivot_data = entry_table.pivot_table(
			index='date',
			columns='dms_site_id',
			values='production_af',
			# this includes all columns
			dropna=False,
		)
		pivot_data.columns = pivot_data.columns.map(lambda x: name_map[x])
		pivot_index = entry_table.pivot_table(
			index='date',
			columns='dms_site_id',
			values='index',
			# this includes all columns
			dropna=False,
		)
		st.data_editor(pivot_data,use_container_width=True,key='entry_table',)
		# st.dataframe(pivot_index)
		# import re
		# cvwd_dict = {
		# 	"CVWD " + re.findall(r'\d+',well)[0].zfill(2):well
		# 	for well in cvwd_list			
		# }
		def add_dates(date_range):
			# create row if it doesn't exist
			for date in arrow.Arrow.span_range('month',date_range[0],date_range[1]):
				date = date[0].format('YYYY-MM-DD')
				for well in name_map.keys():
					if table.df.pipe(
						lambda df:df.loc[(df['dms_site_id']==well) & (df['date']==date)]
						).shape[0] == 0:
						table.append({
							'dms_site_id':well,
							'date':date,
							'production_af':None,
						})


		date_range = [
			arrow.get('1990-01-01'),
			arrow.get('2024-01-01'),
			]
		# if st.button('Add Dates'):
		# 	add_dates(date_range)

		# entry_table =pd.DataFrame(
		# 	data=well_data,
		# 	index=well_data['date'],
		# )
		# # st.markdown(entry_table)
		# st.data_editor(
		# 	entry_table,
		# 	# column_order=[
		# 	# 	'dms_site_id',
		# 	# 	'date',
		# 	# 	'production_af',
		# 	# 	],
		# 	hide_index=True,
		# 	use_container_width=True,

		# 	)
		
		def apply_changes():
			changed_values = st.session_state['entry_table']['edited_rows']
			col = 'production_af'
			for k, v in changed_values.items():
				for well, val in v.items():
					# st.markdown(f"Changing {well} to {val}")
					index = pivot_index.iloc[k][r_name_map[well]]
					# st.markdown(f"Index: {index}")
					row = table.df.pipe(lambda df: df.loc[df['index']==int(index)]).iloc[0]
					table.change(row, col, val, index_col="index")
					# table.change(row, "source",st.session_state["source"],index_col="index")











		show_edits(entry_table)
		if st.button('Add'):
			apply_changes()
			st.rerun()
					# st.markdown(f"CVWD Wells: {well_list}")
		# df = entry_table.pipe(lambda df:df.loc[df['dms_site_id'].isin(cvwd_dict.keys())])
		# df['name'] = df['dms_site_id'].map(cvwd_dict)
		# st.dataframe(df)
		# pivot_table = df.pivot_table(
		# 	index='date',
		# 	columns='name',
		# 	values='production_af',
		# 	# this includes all columns
		# 	dropna=False,
		# )
		# # make column order CVWD List
		# pivot_table = pivot_table[cvwd_list]
		# st.dataframe(pivot_table)

	if table_name == 'Well Names':
		entry_table = table.df
		# .sort_values('date').pivot_table(
		# 	index='dms_site_id',
		# 	columns='date',
		# 	values='production_af',
		# )
		# # entry_table = table.df
		# date_format = "MMM-YY"
		# entry_table.columns = entry_table.columns.map(lambda x: arrow.get(x).format(date_format))

		well_ids = Table('CB_well_info').df['dms_site_id'].unique()
		def add_row():
			st.markdown(f"Adding row for {st.session_state['new_row']}")
			change = {
				'dms_site_id':st.session_state['new_row'],
			}

			# change = {col_name:None for col_name in col_names}
			# col_names = entry_table.columns.tolist()
			# change['date'] = date

			table.append(change)
			# st.rerun()

		st.selectbox('Add row for well',well_ids,key='new_row')
		st.button('Add row',on_click=add_row,use_container_width=True)


		column_config = {
			'dms_site_id':st.column_config.Column(
				label='DMS Site ID',
				disabled=True,
			),
		}
		column_order = [
			'dms_site_id',
			'agency',
			'name',
			'name_production',
			'name_wds',
			'primary']
		st.data_editor(
			entry_table,
			column_order=column_order,
			column_config=column_config,
			use_container_width=True,
			key='entry_table',
			hide_index=True,
			# num_rows='dynamic',
			)

		def apply_changes():
			changed_values = st.session_state['entry_table']['edited_rows']
			for k,v in changed_values.items():
				row = entry_table.iloc[k]
				for column,value in v.items():
					table.change(row,column,value,index_col='index')
					# for column,value in v.items():
					# 	table.change(row,column,value,index_col='index')
					# table.change(row=row,column='source',new_value=source_pdf,index_col='index')





		show_edits(entry_table)	
		if st.button('Add'):
			apply_changes()


	if table_name == 'Well Info':
		column_config = {
			'dms_site_id':st.column_config.Column(
				label='DMS Site ID',
				disabled=True,
			),
			'Monitor_By':st.column_config.Column(
				label='Monitoring Agency',
			),
			'LocalSite_ID':st.column_config.Column(
				label='Local Site ID',
			),
			'SWN':st.column_config.Column(
				label='State Well Number',
			),
			'Site_Code':st.column_config.Column(
				label='Site Code',
			),
			'RPE':st.column_config.Column(
				label='Reference Point Elevation',
			),
			'GSE':st.column_config.Column(
				label='Ground Surface Elevation',
			),
			'TotalWell_Depth':st.column_config.Column(
				label='Total Well Depth',
			),
			'perf_top':st.column_config.Column(
				label='Perforation Top',
			),	
			'perf_bottom':st.column_config.Column(
				label='Perforation Bottom',
			),
			'WellStatus':st.column_config.SelectboxColumn(
				label='Well Status',
				options=['Active','Inactive','Abandoned','Undetermined'],
				required=True,
			),
			# 'perf_bottom':st.column_config.Column(
			# 	label='Perforation Bottom',
			# ),
		
			}
		entry_table = table.df
		entry_table.index = entry_table['dms_site_id']
		st.data_editor(
			entry_table,
			column_order=[
				'dms_site_id',
				'Monitor_By',
				'LocalSite_ID',
				'sdwis_system',
				'sdwis_well',
				'SWN',
				'Site_Code',
				'RPE',
				'GSE',
				'TotalWell_Depth',
				'perf_top',
				'perf_bottom',
				'WellStatus',
			],
			key='entry_table',
			column_config=column_config,
			# hide_index=True,
			use_container_width=True)
		
		def apply_changes():
			changed_values = st.session_state['entry_table']['edited_rows']
			for k,v in changed_values.items():
				row = entry_table.iloc[k]
				for column,value in v.items():
					table.change(row,column,value,index_col='index')

		show_edits(entry_table)	

		if st.button('Add'):
			apply_changes()
			st.rerun()



	elif table_name == 'Water Quality':
		column_config = {
			# 'dms_site_id':st.column_config.Column(
			# 	label='DMS Site ID',
			# 	disabled=True,
			# ),
			'date':st.column_config.DateColumn(
				label='Measurement Date',
			),
			'result':st.column_config.Column(
				label='Result',
			),
			"constituent":st.column_config.Column(
				label='Constituent',
			),
		}
		well_id = st.selectbox('Well ID',table.df['dms_site_id'].unique())
		# constituent = st.selectbox('Constituent',table.df['constituent'].unique())

		entry_table = table.df.pipe(
			lambda df:df[
				(df['dms_site_id']==well_id)
				# & (df['constituent']==constituent)
				]
		).sort_values(['date'])
		# edit_table['meas_date'] = pd.to_datetime(edit_table['meas_date'])
		# edit_table['meas_date'] = edit_table['meas_date'].apply(lambda x: arrow.get(x).format('YYYY-MM-DD'))

		entry_table['date'] = entry_table['date'].apply(lambda x: arrow.get(x).date())
		
		st.data_editor(
			entry_table,
			column_order=[
				# 'dms_site_id',
				'date',
				# 'well_name',
				'constituent',
				'result',
				],
			hide_index=True,
			column_config=column_config,
			key='entry_table',
			num_rows="dynamic",
			use_container_width=True)
		
		def apply_changes():
			added_values = st.session_state['entry_table']['added_rows']
			for value in added_values:
				value['dms_site_id'] = well_id
				table.append(value,index_col='index')

			changed_values = st.session_state['entry_table']['edited_rows']
			for k,v in changed_values.items():
				row = entry_table.iloc[k]
				for column,value in v.items():
					table.change(row,column,value,index_col='index')

		show_edits(entry_table)	
		if st.button('Add'):
			apply_changes()
		# if entry_table.shape[0] > 0:
		# 	# plot edit_table
		# 	from districts.cucamonga.figures import Figure
		# 	from districts.cucamonga.general import Data,Wells
		# 	# st.markdown([well_id])
		# 	well_data = Wells([well_id])
		# 	# st.dataframe(well_data.well_depth_to_water)
		# 	F = Figure(well_data)
		# 	fig = F.mpl_depth_to_water(
		# 		# start_date=start_date,
		# 		# end_date=end_date
		# 		)
		# 	fig.tight_layout()
		# 	st.pyplot(fig)
			


	elif table_name == 'Well Water Levels':
		column_config = {
			'dms_site_id':st.column_config.Column(
				label='DMS Site ID',
				disabled=True,
			),
			'meas_date':st.column_config.DateColumn(
				label='Measurement Date',
			),
			'meas_depth':st.column_config.Column(
				label='Measurement Depth',
			),
		}
		well_id = st.selectbox('Well ID',table.df['dms_site_id'].unique())

		entry_table = table.df.pipe(
			lambda df:df[df['dms_site_id']==well_id]
		).sort_values(['meas_date','dms_site_id'])
		# edit_table['meas_date'] = pd.to_datetime(edit_table['meas_date'])
		# edit_table['meas_date'] = edit_table['meas_date'].apply(lambda x: arrow.get(x).format('YYYY-MM-DD'))
		entry_table['meas_date'] = entry_table['meas_date'].apply(lambda x: arrow.get(x).date())
		
		st.data_editor(
			entry_table,
			column_order=[
				# 'dms_site_id',
				'meas_date',
				'meas_depth',
				],
			hide_index=True,
			column_config=column_config,
			key='entry_table',
			use_container_width=True)
		show_edits(entry_table)	
		
		if entry_table.shape[0] > 0:
			# plot edit_table
			from districts.cucamonga.figures import Figure
			from districts.cucamonga.general import Data,Wells
			# st.markdown([well_id])
			well_data = Wells([well_id])
			# st.dataframe(well_data.well_depth_to_water)
			F = Figure(well_data)
			fig = F.mpl_depth_to_water(
				# start_date=start_date,
				# end_date=end_date
				)
			fig.tight_layout()
			st.pyplot(fig)
			

	elif table_name == 'Well Production':
		# st.markdown(table)
		df = Table(tables['Well Names']).df
		# df['well_name'] = df['name'] + ' - ' + df['agency'] + ' - (' + df['dms_site_id'] + ")"
		df['well_name'] = df['name'] + ' - (' + df['dms_site_id'] + ")"

		select_type = st.radio('Select Type',(
			# 'All',
			'Agency',
			'Well',
			),horizontal=True)
		# if select_type == 'All':
		# 	data_table = table.df
		
		if select_type == 'Well':
			well_names = df['well_name'].unique()
			select_well_names = st.multiselect('Well Names',well_names,default=well_names)
			dms_site_ids = df[df['well_name'].isin(select_well_names)]['dms_site_id'].unique()
			data_table = table.df.pipe(lambda df:df.loc[df['dms_site_id'].isin(dms_site_ids)])
		
		elif select_type == 'Agency':
			# agency = df['agency'].unique()
			# select_agency = st.selectbox('Agency',agency)
			select_agency = agency_names[st.session_state['agency']]
			dms_site_ids = df[df['agency'].isin([select_agency])]['dms_site_id'].unique()
			data_table = table.df.pipe(lambda df:df.loc[df['dms_site_id'].isin(dms_site_ids)])
		
		
		
		entry_table = data_table.sort_values('date').pivot_table(
			index='dms_site_id',
			columns='date',
			values='production_af',
			# this includes all columns
			dropna=False,
		)
		# add well name to entry table
		# entry_table = entry_table.set_index('well_name')

		# entry_table = table.df
		date_format = "MMM-YY"
		entry_table.columns = entry_table.columns.map(lambda x: arrow.get(x).format(date_format))

		date_add = st.radio('Add Date',['Water Year','Month'],horizontal=True)
		
		if date_add == 'Month':
			def add_row():
				date = arrow.get(st.session_state['new_date'],date_format).format("MM/DD/YYYY")
				st.markdown(f"Adding column for {date}")
				row_names = data_table['dms_site_id'].unique()
				for row_name in row_names:
					change = {
						'dms_site_id':row_name,
						'date':date,
						'production_af':None,
					}
					table.append(change)
				# st.rerun()

			st.text_input('Add column for month',placeholder=date_format,key='new_date')
			st.button('Add column',on_click=add_row,use_container_width=True)
		if date_add == 'Water Year':
			def add_year():
				# add all months in water year
				year = st.session_state['new_date']
				for month in range(1,13):
					if month >= 10:
						date = arrow.get(f"{month} {int(year)-1}","M YYYY").format("MM/DD/YYYY")
					else:
						date = arrow.get(f"{month} {year}","M YYYY").format("MM/DD/YYYY")

					st.markdown(f"Adding column for {date}")
					row_names = data_table['dms_site_id'].unique()
					for row_name in row_names:
						change = {
							'dms_site_id':row_name,
							'date':date,
							'production_af':None,
						}
						table.append(change)
				# st.rerun()

			st.text_input('Add columns for water year',placeholder="YYYY",key='new_date')
			st.button('Add Year',on_click=add_year,use_container_width=True)


		entry_table = entry_table.merge(
			df[['dms_site_id','well_name']],
			on='dms_site_id',
			how='left',
		)
		entry_table = entry_table.set_index('well_name')

		column_config = {
			'well_name':st.column_config.Column(
				label='Well Name',
				disabled=True,
			),
			'dms_site_id':None,
		}
		st.data_editor(
			entry_table,
			column_config=column_config,
			use_container_width=True,
			key='entry_table',
			# hide_index=True,
			# num_rows='dynamic',
			)
		
		def apply_changes():
			changed_values = st.session_state['entry_table']['edited_rows']
			index_name = 'dms_site_id'
			column_name = 'date'
			value_name = 'production_af'
			for k,v in changed_values.items():
				row = entry_table.iloc[k]
				# st.dataframe(row,use_container_width=True)

				for col,value in v.items():
					column = arrow.get(col,date_format).format("YYYY-MM-DD")
					index = row['dms_site_id']
					rows = table.df.pipe(lambda df:df.loc[(df[index_name] == index) &(df[column_name] == column)])
					# st.dataframe(rows,use_container_width=True)
					if rows.shape[0] == 1:
						row = rows.iloc[0]
						table.change(
							row=row,
							column=value_name,
							new_value=value,
							index_col='index'
							)
					else:
						st.write(f'Error: {rows.shape[0]} rows found')

		show_edits(entry_table)	

		if st.button('Add'):
			apply_changes()
			# st.rerun()

