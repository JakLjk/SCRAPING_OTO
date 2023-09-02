from ..webhook import db
from ..webhook.db_model import raw_offer_data

from config import DBTableConfig


def add_raw_data_to_db(raw_data, used_link):
    new_raw_offer = raw_offer_data(
        Raw_Data = raw_data,
        Used_Link=used_link)
    db.session.add(new_raw_offer)
    db.session.commit()