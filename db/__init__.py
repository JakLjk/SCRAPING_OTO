import json
import os

import sqlalchemy as db
from sqlalchemy import MetaData
from sqlalchemy.orm import Session
from sqlalchemy.sql import text

from .dbschema import metadata_obj, links_table, raw_offer_data_table

 
# loading db credentials
CREDS_PATH = os.path.join(os.path.dirname(__file__), "credentials.json")

with open(CREDS_PATH) as file:
    creds = json.load(file)

__db_username = creds["DB_USERNAME"]
__db_password = creds["DB_PASSWORD"]
__host = creds["DB_HOST"]
__database = creds["DATABASE_NAME"]

# engine = db.create_engine(f"mysql+mysqlconnector://{__db_username}:{__db_password}@{__host}/{__database}", echo=False)
# ("mariadb+mariadbconnector://app_user:Password123!@127.0.0.1:3306/company"
print('x')
engine = db.create_engine(f"mariadb+mariadbconnector://{__db_username}:{__db_password}@{__host}/{__database}",echo=False)
# with Session(engine) as session:
    
#     session.execute(text('set global max_allowed_packet=67108864'))


# Checking if connection is properly established
with engine.connect():
    pass
