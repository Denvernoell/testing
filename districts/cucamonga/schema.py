import streamlit as st
import graphviz

def database_schema():
	s = graphviz.Digraph(
		name='db_schema',
		# filename='structs.gv',
		engine='neato',
		graph_attr={
			'rankdir': 'LR',
			'splines':'true',
			},
		node_attr={
			'shape': 'plaintext',
			# 'shape': 'box',
			'fontsize': '18',
			'fontname': 'Arial',
			# 'rank': 'same',
			},
		)
	
	class GVTable:
		def __init__(self,table_name,columns):
			self.table_name = table_name
			self.columns = columns
			self.get_s()
			# self.rows = []
		
		def get_s(self):
			# txt = f'<TR><TD align="center" bgcolor="lightgrey">{self.table_name}</TD></TR>'
			txt = f'<TR><TD center="true" bgcolor="lightgrey">{self.table_name}</TD></TR>'
			
			for col in self.columns:
				txt += f'<TR><TD align="left" PORT="{col}">{col}</TD></TR>'
			s.node(
				f'{self.table_name}',f'''<
				<TABLE BORDER="1" CELLBORDER="1" CELLSPACING="0">
				{txt}
				</TABLE>>''')
	
	GVTable('CB_well_info',['DMS Site ID','State Well Number',"Site Code",'Perf Top','Perf Bottom','geometry'])
	GVTable('CB_well_names',['DMS Site ID','Agency','Name','Primary'])
	GVTable('CB_well_production',['DMS Site ID','Date','Production (AF)'])
	GVTable('CB_well_water_levels',['DMS Site ID','Date','Water Surface Elevation'])
	s.edges([
		('CB_well_info:DMS Site ID', 'CB_well_names:DMS Site ID'),
		('CB_well_info:DMS Site ID', 'CB_well_production:DMS Site ID'),
		('CB_well_info:DMS Site ID', 'CB_well_water_levels:DMS Site ID'),
		])
	st.graphviz_chart(s,use_container_width=True)

def main():
	# create_graph()
	st.markdown('## Database Schema')
	database_schema()