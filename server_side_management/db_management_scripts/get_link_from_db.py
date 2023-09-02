from ..webhook.db_model import links
from ..webhook import db
from config import DBTableConfig, OperationTypes

def get_link_from_db():
    link = (links
            .query
            .filter(links.Scrape_Status == \
                       DBTableConfig.links_table_scrape_status_not_scraped)
            .filter(links.Link_Health_Status != OperationTypes.link_health_status_broken)).first()
    if link:
        link.Scrape_Status = DBTableConfig.links_table_scrape_status_being_scraped
        db.session.commit()
        return link.Link
    else:
        raise ValueError("No link available for scrape")
    


def update_scrape_status(link, new_status):
    link = (links
        .query
        .filter(links.Link==link)
        .first())
    link.Scrape_Status = new_status
    db.session.commit()

def update_health_status(link, new_status):
    link = (links
        .query
        .filter(links.Link==link)
        .first())
    link.Scrape_Status = new_status
    db.session.commit()
    