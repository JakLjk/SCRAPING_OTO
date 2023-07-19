import json
import os

import sqlalchemy as db
from sqlalchemy import MetaData
from .dbschema import metadata_obj, links_table, raw_offer_data_table
# loading db credentials
creds_path = os.path.join(os.path.dirname(__file__), "credentials.json")
with open(creds_path) as file:
    creds = json.load(file)

__db_username = creds["DB_USERNAME"]
__db_password = creds["DB_PASSWORD"]
__host = creds["DB_HOST"]
__database = creds["DATABASE_NAME"]

engine = db.create_engine(f"mysql+mysqlconnector://{__db_username}:{__db_password}@{__host}/{__database}",
                        echo=False)
# Checking if connection is properly established
engine.connect()
