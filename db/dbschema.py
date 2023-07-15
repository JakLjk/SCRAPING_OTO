from sqlalchemy import MetaData, Table, Column, Integer, String, Date, Text, Boolean

metadata_obj = MetaData()

# Table schema of db
links_table = Table(
    "links",
    metadata_obj,
    Column("ID_L", Integer, autoincrement=True, primary_key=True),
    Column("Scrape_Date", Date),
    Column("Link", Text),
    Column("Scrape_Status", Text)

)