from fastapi import FastAPI, Response, Query
from districts.cucamonga.data.test_database import Well, Agency, engine
from districts.cucamonga.data.supabase_database import CB_well_info, CB_well_names,engine
from districts.cucamonga.data.supabase_database import engine as hengine
from sqlmodel import Session, select
from typing import List, Optional, Annotated

app = FastAPI()

@app.get(
		"/hwells/",
		summary="Read wells from postgres",
		description="Read all wells or a subset of wells by id",
		response_model=List[CB_well_info],
		)
async def read_hwells(ids: Annotated[list[str],Query()]=[]):
	with Session(hengine) as session:
		statement = select(CB_well_info)
		if ids != []:
			# statement = statement.where(CB_well_info.index.in_(ids))
			statement = statement.where(CB_well_info.dms_site_id.in_(ids))
		result = session.exec(statement)
		wells = result.all()
		return wells



# *Completed
@app.get(
		"/wells/",
		summary="Read wells",
		description="Read all wells or a subset of wells by id",
		response_model=List[Well],
		)
async def read_wells(ids: Annotated[list[int],Query()]=[]):
	with Session(engine) as session:
		statement = select(Well)
		if ids != []:
			statement = statement.where(Well.id.in_(ids))
		result = session.exec(statement)
		wells = result.all()
		return wells


@app.get(
		"/well/",
		response_model=Well
		)
def read_well(id: int, response: Response):
	with Session(engine) as session:
		statement = select(Well).where(Well.id == id)
		result = session.exec(statement)
		well = result.one_or_none()
		if well is None:
			response.status_code = 404
			return {"detail": "Well not found"}
		return well

@app.post(
		"/wells/add/",
		description="Add attributes for new wells",
		response_model=Well,
		status_code=201,
		)
def add_well(well: Well, response: Response):
	print(well)
	with Session(engine) as session:
		session.add(well)
		session.commit()
		session.refresh(well)
		return well
	
@app.get(
		"/agencies/",
		response_model=List[Agency],
		)
async def read_agencies(ids: Annotated[list[int],Query()]=[]):
	with Session(engine) as session:
		if ids == []:
			statement = select(Agency)
		else:
			statement = select(Agency).where(Agency.id.in_(ids))
		result = session.exec(statement)
		agencies = result.all()
		return agencies


# TODO Not Completed
@app.put("/wells/update/{id}/",response_model=Well)
def update_well(well_id: int,data:Well, response: Response):
	with Session(engine) as session:
		statement = select(Well).where(Well.id == well_id)
		result = session.exec(statement)
		well = result.one_or_none()
		if well is None:
			response.status_code = 404
			return {"detail": "Well not found"}
		for key,value in data.dict().items():
			setattr(well,key,value)
		session.add(well)
		session.commit()
		return well

@app.get("/agency/{agency_id}")
def read_agency( response: Response):
	with Session(engine) as session:
		statement = select(Agency).where(Agency.id == agency_id)
		result = session.exec(statement)
		agency = result.one_or_none()
		if agency is None:
			response.status_code = 404
			return {"detail": "Agency not found"}
		return agency

@app.get("/agency/{agency_id}/wells")
def read_agency_wells(agency_id: int, response: Response):
	with Session(engine) as session:
		statement = select(Well).where(Well.agency_id == agency_id)
		result = session.exec(statement)
		wells = result.all()
		if wells is None:
			response.status_code = 404
			return {"detail": "Agency not found"}
		return wells

@app.get("/well/{well_id}/agency")
def read_well_agency(well_id: int, response: Response):
	with Session(engine) as session:
		statement = select(Well).where(Well.id == well_id)
		result = session.exec(statement)
		well = result.one_or_none()
		if well is None:
			response.status_code = 404
			return {"detail": "Well not found"}
		return well.agency


# !Depreciated


@app.get(
		"/well/{well_id}/agency/name",
		
		# include_in_schema=False,
		deprecated=True,
		
		)
def read_well_agency(well_id: int, response: Response):
	with Session(engine) as session:
		statement = select(Well).where(Well.id == well_id)
		result = session.exec(statement)
		well = result.one_or_none()
		if well is None:
			response.status_code = 404
			return {"detail": "Well not found"}
		return well.agency
