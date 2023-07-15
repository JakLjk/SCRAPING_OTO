import sqlalchemy as db
from sqlalchemy import MetaData
from .dbschema import metadata_obj, links_table

# TODO add credentials json loader

__db_username = "root"
__db_password = ""
__host = "localhost"
__database = "otomoto_data"

engine = db.create_engine(f"mysql+mysqlconnector://{__db_username}:{__db_password}@{__host}/{__database}", echo=True)
# Checking if connection is properly established
engine.connect()
