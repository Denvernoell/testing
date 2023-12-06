import httpx
import pandas as pd


class System:
    def __init__(self) -> None:
		url = 'https://sdwis.waterboards.ca.gov/PDWW/JSP/WSamplingResultsByStoret.jsp?'
		params = {
				'SystemNumber':'3610018',
				'tinwsys_is_number':'3782',
				'FacilityID':'002',
				'WSFNumber':'10343',
				'SamplingPointID':'002',
				'SystemName':'CUCAMONGA+VALLEY+WATER+DISTRICT',
				'SamplingPointName':'WELL+01',
				'Analyte':'1040',
				'ChemicalName':'',
				'begin_date':'',
				'end_date':'',
				'mDWW':''
				}
		R = httpx.get(
			url,
			params=params
		)
