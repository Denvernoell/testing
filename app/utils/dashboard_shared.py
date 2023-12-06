import streamlit as st
import sys

import plotly.graph_objects as go
import pandas as pd

import base64
import io

import arrow
from importlib import import_module

import geopandas as gpd
import httpx
from shapely.geometry import LineString, LinearRing, MultiPolygon,Point
from shapely.ops import unary_union

#? what is the difference between feature and map servers?
# FeatureServer
# MapServer
servers = {
		'cimis':'https://gis.water.ca.gov/arcgis/rest/services/Climatology/i04_CIMIS_Weather_Stations/MapServer/0',
		"Lakes and Reservoirs":'https://gis.water.ca.gov/arcgis/rest/services/InlandWaters/NHD_Major_Lakes_and_Reservoirs/MapServer/0',
		"Rivers":'https://gis.water.ca.gov/arcgis/rest/services/InlandWaters/NHD_Major_Rivers/MapServer/0',
		"Rivers and Creeks":'https://gis.water.ca.gov/arcgis/rest/services/InlandWaters/NHD_Major_Rivers_and_Creeks/MapServer/0',
		"Local Canals and Aqueducts":'https://gis.water.ca.gov/arcgis/rest/services/InlandWaters/i12_Canals_and_Aqueducts_local/MapServer/0',
		"Federal Canals and Aqueducts":'https://gis.water.ca.gov/arcgis/rest/services/InlandWaters/i12_Canals_and_Aqueducts_Federal/MapServer/0',
		"Water Districts":'https://gis.water.ca.gov/arcgis/rest/services/Boundaries/i03_WaterDistricts/MapServer/0',
		"Groundwater Sustainability Agencies":'https://gis.water.ca.gov/arcgis/rest/services/Boundaries/i03_Groundwater_Sustainability_Agencies/MapServer/0',
		"PLSS T&R":"https://gis.conservation.ca.gov/server/rest/services/Base/BASE_PLSS/MapServer/0",
		"PLSS T&R&S":"https://gis.conservation.ca.gov/server/rest/services/Base/BASE_PLSS/MapServer/1",
		"Water Data Library Stations":"https://gis.water.ca.gov/arcgis/rest/services/Geoscientific/i08_GroundwaterStations_EnterpriseWaterManagement/MapServer/0",
		"Stream Reaches":"https://gis.water.ca.gov/arcgis/rest/services/Geoscientific/i08_C2VSimFG_Stream_Reaches/MapServer/0",
		"Stream Nodes":"https://gis.water.ca.gov/arcgis/rest/services/Geoscientific/i08_C2VSimFG_Stream_Nodes/MapServer/0",
}


class GIS_REST:
	def __init__(self,base_url) -> None:
		self.base_url = base_url


	def get_options(self):
		r = httpx.get(self.base_url,params={
			'where':'1=1',
			'outFields':'*',
			'outSR':'4326',
			'f':'json'
			})
		# print(r.url)
		J = r.json()
		# J.keys()
		
		# st.markdown([i for i in J.keys()])
		# st.dataframe(pd.DataFrame(J['fields']),use_container_width=True)

		# st.markdown(J['fields'])
		# st.markdown(J['indexes'])

		vals = J['drawingInfo']['renderer']['uniqueValueInfos']
		return [i['label'] for i in vals]

	def get_gdf(self,where='1=1',geometry=None,geometry_bounds=None):

		if geometry:
			bounds = [str(x) for x in geometry.total_bounds]
			geometry_bounds = ",".join(bounds)
		
			r = httpx.get(self.base_url+ "/query",params={
				'where':where,
				'geometry':geometry_bounds,
				'geometryType':'esriGeometryEnvelope',
				'inSR':'4326',
				'spatialRel':'esriSpatialRelIntersects',
				'outFields':'*',
				'outSR':'4326',
				'f':'json'
				})
		elif geometry_bounds:
			r = httpx.get(self.base_url+ "/query",params={
				'where':where,
				'geometry':geometry_bounds,
				'geometryType':'esriGeometryEnvelope',
				'inSR':'4326',
				'spatialRel':'esriSpatialRelIntersects',
				'outFields':'*',
				'outSR':'4326',
				'f':'json'
				})

		else:
			r = httpx.get(self.base_url+ "/query",params={
				'where':where,
				'outFields':'*',
				'outSR':'4326',
				'f':'json'
				})

				# bounds = [str(x) for x in geometry.bounds.iloc[0]]
			self.url = r.url

		# !this was added to test servers that dont return features
		try:
			# st.markdown(r)
			J = r.json()
			# st.markdown(J)
			# print([i for i in J.keys()])
			df = pd.DataFrame(J['features'])
			df_info = df['attributes'].apply(pd.Series)
			df_geometry = df['geometry'].apply(pd.Series)
			# st.dataframe(df)

			# ring
			if 'rings' in df_geometry.columns:
				make_shp = lambda x: unary_union([LinearRing(i) for i in x])
				gdf = gpd.GeoDataFrame(
					df_info,
					# geometry=gpd.points_from_xy(x=df_geometry['x'],y=df_geometry['y'],crs="EPSG:4326")
					geometry=df_geometry['rings'].apply(make_shp),
					).set_crs("EPSG:4326")
				
			elif 'paths' in df_geometry.columns:
				# from IPython.display import display
				# display(df_geometry.head())
				make_shp = lambda x: unary_union([LineString(i) for i in x])
				gdf = gpd.GeoDataFrame(
					df_info,
					# geometry=gpd.points_from_xy(x=df_geometry['x'],y=df_geometry['y'],crs="EPSG:4326")
					geometry=df_geometry['paths'].apply(make_shp),
					).set_crs("EPSG:4326")
			# point
			elif 'x' in df_geometry.columns:
				gdf = gpd.GeoDataFrame(
					df_info,
					geometry=gpd.points_from_xy(x=df_geometry['x'],y=df_geometry['y'],crs="EPSG:4326")
					)
			

			else:
				# gdf = df_geometry.columns
				print(df_geometry.columns)
				raise Exception("Unknown geometry type")
			self.gdf = gdf
			self.df = gdf.drop(columns='geometry')

			#? Look into using these
			# gdf = get_cdec_gdf().pipe(lambda x: x.loc[~x['geometry'].is_empty])
			# correct_lat = lambda x: x if x < 0 else -x
			# gdf['geometry'] = gdf['geometry'].apply(lambda x: Point(correct_lat(x.x),x.y))
		except Exception as e:
			print(r.url)
			print(r.text)
			print(e)
			# print(r.url)
			# return r
			# raise Exception("Error in get_gdf")

class District:
	def __init__(self,name,folder,pages):
		self.name = name
		self.pages = pages
		self.folder = folder

	def homepage(self):
		st.header(self.name)
		page = self.pages[st.sidebar.radio('Page', list(self.pages.keys()))]
		module = import_module(f'districts.{self.folder}.{page}')

		module.main()
	



class Components:
	def __init__(self,name):
		self.name = name
		st.set_page_config(
			page_title=f"{self.name} Data Management System",
			page_icon="📊",
			layout="wide",
			)
		# self.header()

	def header(self):
		# st.title(f"{self.name} Data Management System")
		st.sidebar.title(f"{self.name} Data Management System")
		# st.markdown("""
		# <style>
		#        .css-18e3th9 {
		#             padding-top: 0rem;
		#             padding-bottom: 0rem;
		#             padding-left: 0rem;
		#             padding-right: 0rem;
		#         }
		#        .css-1d391kg {
		#             padding-top: 3rem;
		#             padding-right: 0rem;
		#             padding-bottom: 3rem;
		#             padding-left: 0rem;
		#         }
		# </style>
		# """, unsafe_allow_html=True)

	def footer(self):
		st.write("---")
		st.markdown(f"[*Provost & Pritchard Consulting Group - 2023*](https://provostandpritchard.com/)")

def month_picker(start_year,end_year):
	year_range = range(start_year,end_year)
	if st.checkbox("Single Month"):
		month = st.selectbox('Month',[arrow.get(f"{i}","M").format('MMMM') for i in range(1,13)])
		year = st.selectbox('Year',year_range)
		return [
			arrow.get(f"{year}-{month}","YYYY-MMMM"),
			arrow.get(f"{year}-{month}","YYYY-MMMM"),
			]
		# return month
	else:
		c1,c2,c3,c4 = st.columns(4)
		with c1:
			start_month = st.selectbox('Start Month',[arrow.get(f"{i}","M").format('MMMM') for i in range(1,13)])
		with c2:
			start_year = st.selectbox('Start Year',year_range,index=0)
		with c3:
			end_month = st.selectbox('End Month',[arrow.get(f"{i}","M").format('MMMM') for i in range(1,13)])
		with c4:
			end_year = st.selectbox('End Year',year_range,index=len(year_range)-1)
		# return [
		# 	arrow.get(f"{start_year}-{start_month}","YYYY-MMMM"),
		# 	arrow.get(f"{end_year}-{end_month}","YYYY-MMMM"),
		# 	]

		# return arrow.get(f"{start_year}-{start_month}","YYYY-M"),arrow.get(f"{end_year}-{end_month}","YYYY-M")						


class User:
	def __init__(self,username,password):
		self.username = username
		self.password = password

def show_pdf(file_path):
	with open(file_path,"rb") as f:
		base64_pdf = base64.b64encode(f.read()).decode('utf-8')
		pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="800" height="800" type="application/pdf"></iframe>'		
		st.markdown(pdf_display, unsafe_allow_html=True)

def download_fig(fig,file_name,label):
	file_path = f"{file_name}.pdf"
	fig.savefig(file_path)
		
	with open(file_path, "rb") as pdf_file:
		PDFbyte = pdf_file.read()

	st.download_button(label=label, 
			data=PDFbyte,
			file_name=f"{file_name}.pdf",
			mime='application/octet-stream')

def download_pdf(file_path,file_name,label):
		
	with open(file_path, "rb") as pdf_file:
		PDFbyte = pdf_file.read()

	st.download_button(label=label, 
			data=PDFbyte,
			file_name=f"{file_name}.pdf",
			mime='application/octet-stream')


def convert_date(df,col):
	df[col] = df[col].pipe(pd.to_datetime)
	return df

def export_df(df,file_name,index=True,header=True):
	towrite = io.BytesIO()
	downloaded_file = df.to_excel(towrite, encoding='utf-8', index=index, header=header)
	towrite.seek(0)  # reset pointer
	b64 = base64.b64encode(towrite.read()).decode()  # some strings
	linko= f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{file_name}">Download excel file</a>'
	# return linko
	st.markdown(linko, unsafe_allow_html=True)

def export_excel(file_name):
	towrite = io.BytesIO()
	downloaded_file = df.to_excel(towrite, encoding='utf-8')
	towrite.seek(0)  # reset pointer
	b64 = base64.b64encode(towrite.read()).decode()  # some strings
	linko= f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{file_name}">Download excel file</a>'
	# return linko
	st.markdown(linko, unsafe_allow_html=True)
class Table:
	# def __init__(self,client,table_name):
	def __init__(self,table_name,client=None):
		"""
		client: supabase connection
		table_name: table name of supabase table
		"""

		if client:
			self.client = client
		else:
			# print(table_name)
			self.client = st.session_state['client']
		
		self.table_name = table_name
		self.table = self.client.table(self.table_name)
		self.refresh()
	
	def __repr__(self) -> str:
		return f"Table Name = {self.table_name}"
	
	def refresh(self):
		self.df = pd.DataFrame(self.client.table(self.table_name).select('*').execute().data)
	
	def append(self,data,index_col='index'):
		"""
		data; dict {"client":"Aliso"}
		"""
		user = st.session_state['user_email']

		
		# st.markdown(max([i[index_col] for i in self.table.select(index_col).execute()]))
		data[index_col] = max([i[index_col] for i in self.table.select(index_col).execute().data]) + 1


		change_log = f'{user} added on {arrow.now().format("YYYY-MM-DD")}'
		data['changelog'] = change_log

		self.table.insert(data).execute()

		# ? Not sure if this is needed
		# self.refresh()

	def change(self,row,column,new_value,index_col='id'):
		user = st.session_state['user_email']
		old_value = row[column]
		import arrow
		change_log = f'{user} changed "{column}" from "{old_value}" to "{new_value}" on {arrow.now().format("YYYY-MM-DD")}'
		# st.write(change_log)
		data = {column:new_value}

		if 'changelog' not in self.df.columns:
			st.warning("No changelog column")

			# self.table.alter(add_column='changelog', data_type='text')
			# self.refresh()
			# row['changelog'] = None
		
		else:
				

			if row['changelog'] is None:
				data['changelog'] = change_log
			else:
				data['changelog'] = row['changelog'] + "\n" + change_log
			# st.markdown(data)
			row_id = row[index_col]

			# st.markdown(row_id)
			self.edit(data,row_id,index=index_col)


	def edit(self,data,row,index='index'):
		"""
		data: dict {"client":"Aliso"}
		locator: list ["id",1]
		"""

		self.table.update(data).eq(index,row).execute()
		
		# ? Not sure if this is needed
		# self.refresh()






	def delete(self,row,index='index'):
		"""
		locator: list ["id",1]
		"""
		self.table.delete().eq(index,row).execute()
		self.refresh()

# class OfflineTable(Table):
# 	def __init__(self, table_name):
# 		import tomli
# 		from supabase import create_client, Client
# 		with open("..\\..\\.streamlit\\secrets.toml",'rb') as f:
# 		# with open(".streamlit\\secrets.toml",'rb') as f:
# 			config = tomli.load(f)
# 		client: Client = create_client(config['supabase_url'],config['supabase_key'])
# 		user = client.auth.sign_in_with_password(
# 					credentials={'email':config['test_email'],'password':config['test_password']}
# 					)
# 		super().__init__(table_name, client=user)

# class Table:
# 	# def __init__(self,client,table_name):
# 	def __init__(self,table_name):
# 		"""
# 		client: supabase connection
# 		table_name: table name of supabase table
# 		"""
# 		# self.client = client
# 		self.client = st.session_state['client']
		
# 		self.table_name = table_name
# 		self.refresh()
	
# 	def __repr__(self) -> str:
# 		return f"Table Name = {self.table_name}"
	
# 	def refresh(self):
# 		self.df = pd.DataFrame(self.client.table(self.table_name).select('*').execute().data)
	
# 	def append(self,data):
# 		"""
# 		data; dict {"client":"Aliso"}
# 		"""
# 		self.client.table(self.table_name).insert(data).execute()
# 		self.refresh()

# 	def edit(self,data,locator):
# 		"""
# 		data: dict {"client":"Aliso"}
# 		locator: list ["id",1]
# 		"""
# 		self.client.table(self.table_name).update(data).eq(locator).execute()
# 		self.refresh()

# 	def delete(self,locator):
# 		"""
# 		locator: list ["id",1]
# 		"""
# 		self.client.table(self.table_name).delete().eq(locator).execute()
# 		self.refresh()


# # def get_table(table_name):
# # 	return pd.DataFrame(st.session_state['client'].table(table_name).select('*').execute().data)

# def convert_date(df,col):
# 	df[col] = df[col].pipe(pd.to_datetime)
# 	return df


# def edit_levels():
# 	st.subheader('Wells and Water Levels')

# 	table = Table('date')
# 	st.experimental_data_editor(table.df,use_container_width=True,num_rows='dynamic',key='date_changes',)
# 	changes = st.session_state["date_changes"]
# 	st.write(changes)
# 	if st.button('Save'):
# 		# # st.session_state['client'].table('date').update(st.session_state["date_changes"]).execute()
# 		# for k,v in changes['edited_cells'].items():
# 		# 	row,col = [int(i) for i in k.split(':')]
# 		# 	# row,col = [int(i) for i in k.split(':')]
# 		# 	st.write(f"Changed {row} -> {col}={v}")

# 		# for change in changes['added_rows']:
# 		# 	for i,data in change.items():
# 		# 		for k,v in data.items():
# 		# 			col = int(k)
# 		# 			st.write(f"Added {col}={v}")
		
# 		# for change in changes['deleted_rows']:
# 		# 	for i,row in change.items():
# 		# 		# delete row
# 		# 		st.write(f"Deleted {row}")
		
# 		# st.write(changes['edited_cells'])
# 		st.write(changes['added_rows'])
# 		st.write(changes['deleted_rows'])
# 		st.success('Saved')