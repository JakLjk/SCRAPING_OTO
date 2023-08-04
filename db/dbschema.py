from sqlalchemy import MetaData, Table, Column, Integer, String, Date, Text, Boolean, DATETIME
from sqlalchemy.dialects.mysql import LONGTEXT
metadata_obj = MetaData()

# Table schema of db
links_table = Table(
    "links",
    metadata_obj,
    Column("ID_L", Integer, autoincrement=True, primary_key=True),
    Column("Scrape_DateTime", DATETIME),
    Column("Link", Text),
    Column("Scrape_Status", Text))

raw_offer_data_table = Table(
    "raw_offer_data",
    metadata_obj,
    Column("ID_O",Integer, autoincrement=True, primary_key=True),
    Column("Scrape_DateTime",DATETIME),
    Column("Raw_Data", LONGTEXT),
    Column("Used_Link", Text),
    Column("ETL_Performed_Status", Boolean))

offers_parsed = Table(
    "offer_details_parsed",
    metadata_obj,
    Column("ID_O_P",Integer, autoincrement=True, primary_key=True),
    Column("Parsing_DateTime",DATETIME),
    Column("Link", Text))