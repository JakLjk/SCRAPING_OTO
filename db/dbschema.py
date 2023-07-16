from sqlalchemy import MetaData, Table, Column, Integer, String, Date, Text, Boolean
from sqlalchemy.dialects.mysql import LONGTEXT
metadata_obj = MetaData()

# Table schema of db
links_table = Table(
    "links",
    metadata_obj,
    Column("ID_L", Integer, autoincrement=True, primary_key=True),
    Column("Scrape_Date", Date),
    Column("Link", Text),
    Column("Scrape_Status", Text))

raw_offer_data_table = Table(
    "raw_offer_data",
    metadata_obj,
    Column("ID_O",Integer, autoincrement=True, primary_key=True),
    Column("DATE",Date),
    Column("Raw_Data", LONGTEXT),
    Column("Used_Link", Text))

