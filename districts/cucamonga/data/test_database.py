from typing import Optional,Any
# https://stackoverflow.com/questions/75084163/use-postgis-geometry-types-in-sqlmodel
from geoalchemy2 import Geometry
# from geoalchemy2.types import Geometry as GeoAlchemyGeometry
from geoalchemy2.types import Geometry as GeoAlchemyGeometry
import geoalchemy2.types as gtypes

from sqlmodel import Field, SQLModel, create_engine, Session, select,Column


class Agency(SQLModel, table=True):
	id: Optional[int] = Field(default=None, primary_key=True)
	name: str
	

class Well(SQLModel, table=True):
	id: int = Field(default=None, primary_key=True)
	agency_id: int = Field(default=None, foreign_key="agency.id")
	geometry: Any = Field(sa_column=Column(Geometry("POINT", srid=4326)))


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(
	sqlite_url,
	echo=False,
	# extend_existing=True,
	)

def create_db_and_tables():
	SQLModel.metadata.create_all(engine)

def add_agencies():		
	with Session(engine) as session:
		cvwd = Agency(id=1,name="Cucamonga Valley Water District")
		sawc = Agency(id=2,name="San Antonio Water Company")
		we = Agency(id=3,name="West End Consolidated Water Company")
		session.add(cvwd)
		session.add(sawc)
		session.add(we)

		session.commit()

def add_wells():		
	with Session(engine) as session:
		w1 = Well(id=1,agency_id=1,LocalSite_ID=1,geometry="POINT(34.1234 -117.1234)")
		w2 = Well(id=2,agency_id=1,LocalSite_ID=2,geometry="POINT(34.2234 -117.2234)")
		session.add(w1)
		session.add(w2)
		session.commit()

def select_wells():		
	with Session(engine) as session:
		# statement = select(Well,Agency).where(Well.agency_id == Agency.id)
		statement = select(Well,Agency).join(Agency)
		results = session.exec(statement)
		for well,agency in results:
			print(well)
			print(agency)
		return [i for i in results]