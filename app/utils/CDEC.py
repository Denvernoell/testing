import httpx
import pandas as pd
import numpy as np

class CDEC:
	def __init__(self,id,date_range) -> None:
		self.id = id
		self.start_date,self.end_date = date_range

	def get_data(self,sensors="20",dur_code="H"):
		R = httpx.get(
			f'https://cdec.water.ca.gov/dynamicapp/req/JSONDataServlet',
			params={
				"Stations":self.id,
				"SensorNums":sensors,
				"dur_code":dur_code,
				"Start":self.start_date,
				"End":self.end_date,
				# "end_date":"now",
			},
			timeout=20,
		)
		self.url = R.url
		# print(R.json())
		df = pd.DataFrame(R.json())
		try:
			df = df.astype({'date':'datetime64[ns]'}).set_index('date')
			df['value'] = df['value'].where(df['value']>-9990,np.nan)
			#! check with ethan if this needs to be shifted
			# df = df.shift(1, freq='H')
			return df
		except Exception as e:
			from IPython.display import display
			display(df)
			print(f'Error getting data for {self.id}')
			print(e)
			return df