from ..webhook import db
from ..webhook.db_model import raw_offer_data

from config import DBTableConfig


def add_raw_data_to_db(raw_data, webpage_style, used_link):
    new_raw_offer = raw_offer_data(
        Raw_Data = raw_data,
        Webpage_Layout_Version = webpage_style,
        Used_Link=used_link,
        ETL_Performed_Status=DBTableConfig.raw_data_table_etl_not_performed)
    db.session.add(new_raw_offer)
    db.session.commit()