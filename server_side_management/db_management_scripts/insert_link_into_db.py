from sqlalchemy import func

from ..webhook import db
from ..webhook.db_model import links

from config import DBTableConfig


def add_link_to_db(input_link):
    link_exists = links.query.filter_by(Link=input_link).first()
    if link_exists:
        raise ValueError("Such link is already present in db")
    else:
        new_link = links(Link=input_link,
              Scrape_Status = DBTableConfig.links_table_scrape_status_not_scraped)
        db.session.add(new_link)
        db.session.commit()



