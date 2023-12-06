import streamlit as st
import pandas as pd

from testing.utils.dashboard_shared import Table
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
	}
	table_name = st.selectbox('Select a table',list(tables.keys()))
	table = Table(tables[table_name])

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
		column_order = ['dms_site_id','agency','name','primary']
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
			'WellStatus':st.column_config.Column(
				label='Well Status',
			),
		
			}

		st.data_editor(
			table.df,
			column_order=[
				'dms_site_id',
				'Monitor_By',
				'LocalSite_ID',
				'SWN',
				'Site_Code',
				'RPE',
				'GSE',
				'TotalWell_Depth',
				'perf_top',
				'perf_bottom',
				'WellStatus',
			],
			column_config=column_config,
			hide_index=True,
			use_container_width=True)

		show_edits(entry_table)	



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

		edit_table = table.df.pipe(
			lambda df:df[df['dms_site_id']==well_id]
		).sort_values(['meas_date','dms_site_id'])
		# edit_table['meas_date'] = pd.to_datetime(edit_table['meas_date'])
		# edit_table['meas_date'] = edit_table['meas_date'].apply(lambda x: arrow.get(x).format('YYYY-MM-DD'))
		edit_table['meas_date'] = edit_table['meas_date'].apply(lambda x: arrow.get(x).date())
		
		st.data_editor(
			edit_table,
			column_order=[
				# 'dms_site_id',
				'meas_date',
				'meas_depth',
				],
			hide_index=True,
			column_config=column_config,
			use_container_width=True)
		show_edits(entry_table)	
		
		if edit_table.shape[0] > 0:
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
		st.markdown(table)

		df = Table(tables['Well Names']).df
		# df['well_name'] = df['name'] + ' - ' + df['agency'] + ' - (' + df['dms_site_id'] + ")"
		df['well_name'] = df['name'] + ' - (' + df['dms_site_id'] + ")"

		select_type = st.radio('Select Type',('All','Well','Agency'),horizontal=True)
		if select_type == 'All':
			data_table = table.df
		
		elif select_type == 'Well':
			well_names = df['well_name'].unique()
			select_well_names = st.multiselect('Well Names',well_names,default=well_names)
			dms_site_ids = df[df['well_name'].isin(select_well_names)]['dms_site_id'].unique()
			data_table = table.df.pipe(lambda df:df.loc[df['dms_site_id'].isin(dms_site_ids)])
		
		elif select_type == 'Agency':
			agency = df['agency'].unique()
			select_agency = st.selectbox('Agency',agency)
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
				for col,value in v.items():
					column = arrow.get(col,date_format).format("YYYY-MM-DD")
					index = row['dms_site_id']
					rows = table.df.pipe(lambda df:df.loc[(df[index_name] == index) &(df[column_name] == column)])
					if rows.shape[0] == 1:
						row = rows.iloc[0]
						# st.dataframe(row,use_container_width=True)
						table.change(
							row=row,
							column=value_name,
							new_value=value,
							index_col='index'
							)

		show_edits(entry_table)	

		if st.button('Add'):
			apply_changes()
			st.rerun()

