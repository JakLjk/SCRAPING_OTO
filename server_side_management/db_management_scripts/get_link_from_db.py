from ..webhook.db_model import links
from ..webhook import db
from config import DBTableConfig

def get_link_from_db():
    link = (links
            .query
            .filter_by(Scrape_Status = \
                       DBTableConfig.links_table_scrape_status_not_scraped)).first()
    if link:
        link.Scrape_Status = DBTableConfig.links_table_scrape_status_being_scraped
        db.session.commit()
        return link.Link
    else:
        raise ValueError("No link available for scrape")
    
def update_link_status():
    pass
    
    