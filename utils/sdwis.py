import pandas as pd
import httpx

from pathlib import Path
import polars as pl

data_path = Path("utils")
wq_systems = pl.read_parquet(data_path / "wq_systems.parquet").to_pandas()

class System:
	def __init__(self,system_number,is_number) -> None:
		self.system_number = system_number
		self.is_number = is_number
		
		import json
		wq_map = json.load(open(data_path.joinpath('sdwis_wq_numbers.json')))
		self.wq_map = {v:k for k,v in wq_map.items()}


		self.site_urls = self.get_site_urls()
		import re
		# lambda col: re.search('WSFNumber=(\d+)',col).group(1)
		# lambda col: re.search('WSFNumber=(\d+)',col)
		def get_wsf_number(col):
			try:
				return re.search('WSFNumber=(\d+)',col).group(1)
			except:
				return None
			
		self.site_urls['WSFNumber'] = self.site_urls['New PS Codes'].apply(get_wsf_number)
	
	def get_details(self):
		# url = 'https://sdwis.waterboards.ca.gov/PDWW/JSP/WaterSystemDetail.jsp?tinwsys_is_number=3782&tinwsys_st_code=CA&counter=0'
		url = 'https://sdwis.waterboards.ca.gov/PDWW/JSP/WaterSystemDetail.jsp'
		R = httpx.get(
			url,
			params={
				# "SystemNumber":self.system_number,
				"tinwsys_is_number":self.is_number,
				"tinwsys_st_code":'CA',
				"counter":'0'
			}
		)
		
		return self.get_df(R)

	def get_df(self,R):
		try:
			dfs = pd.read_html(R.text)
			# df.columns = df.iloc[0]
			return dfs
		except:
			return R.url
			return R.text
	
	def get_site_urls(self):
		df = pd.read_html(
			f"https://sdwis.waterboards.ca.gov/PDWW/JSP/NMonitoringSchedules.jsp?tinwsys_is_number={self.is_number}&tinwsys_st_code=CA&ReportFormat=SR",
			extract_links="body",
		)[0]

		# use link text if it exists

		df.columns = [c[2] for c in df.columns]
		return df[:-2].applymap(lambda x: x[1] if None not in x else x[0])
		

	def get_sites(self):
		# https://sdwis.waterboards.ca.gov/PDWW/JSP/NMonitoringSchedules.jsp?tinwsys_is_number=3782&tinwsys_st_code=CA&ReportFormat=SR
		# https://sdwis.waterboards.ca.gov/PDWW/JSP/WaterSystemFacilities.jsp?tinwsys_is_number=3782&tinwsys_st_code=CA

		url = "https://sdwis.waterboards.ca.gov/PDWW/JSP/NMonitoringSchedules.jsp"
		params = {
			"tinwsys_is_number":self.is_number,
			"tinwsys_st_code":'CA',
			"ReportFormat":'SR'
		}
		R = httpx.get(
			url=url,
			params=params,
		)
		df = self.get_df(R)[0]
		df.columns = [c[2] for c in df.columns]
		return df


	def get_wq(self,point_name,analyte_name=None,start_date=None):
		url = 'https://sdwis.waterboards.ca.gov/PDWW/JSP/WSamplingResultsByStoret.jsp?'
		import arrow
		if start_date:
			start_date = start_date.strftime('%m/%d/%Y')
			end_date = arrow.now().format('MM/DD/YYYY')
		else:
			start_date = ''
			end_date = ''
		row = self.site_urls[self.site_urls['Sample Point Name']==point_name].iloc[0]
		params = {
				'SystemNumber':self.system_number,
				'tinwsys_is_number':self.is_number,
				'FacilityID':row['Facility ID'],
				'WSFNumber':row['WSFNumber'],
				'SamplingPointID':row['Sample Point ID'],

				# 'SystemName':'CUCAMONGA+VALLEY+WATER+DISTRICT',
				'SamplingPointName':row['Sample Point Name'],
				'ChemicalName':'',
				'begin_date':start_date,
				'end_date':end_date,
				'mDWW':'',
				}
		# https://sdwis.waterboards.ca.gov/PDWW/JSP/WSamplingResultsByStoret.jsp?SystemNumber=3610018&SystemName=CUCAMONGA+VALLEY+WATER+DISTRICT&tinwsys_is_number=3782&SamplingPointName=WELL+01&SamplingPointID=002-002-10343&mDWW=null&Analyte=1040&ChemicalName=NITRATE&begin_date=09%2F19%2F2020&end_date=09%2F30%2F2023&Generate+Report=Generate+Report
				
		if analyte_name:
			params['Analyte'] = [self.wq_map[analyte_name]]
		R = httpx.get(
			url,
			params=params
		)

		
		# import streamlit as st
		# st.markdown(self.get_df(R))
		df = self.get_df(R)[0]
		# remove top column row
		df.columns = [' - '.join(col) if col[0] != col[1] else col[1] for col in df.columns ]
		# drop last 3 rows
		return df[:-3]
