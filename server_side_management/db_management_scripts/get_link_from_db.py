from ..webhook.db_model import links
from ..webhook import db
from config import DBTableConfig, OperationTypes, Config

def get_link_from_db():
    link = (links
            .query
            .filter(links.Scrape_Status == \
                       DBTableConfig.links_table_scrape_status_not_scraped)
            # .filter(links.Failed_Times < Config.LinksScrapingSetup.MAX_ACCEPTED_SUBSEQUENT_LINK_DB_FAILED_COLUMN_INTEGER)
            ).first()
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

def update_error_message(link, message):
    link = (links
                .query
                .filter(links.Link==link)
                .first())
    link.Error_Message = message
    db.session.commit()

def update_health_status(link, new_status):
    link = (links
        .query
        .filter(links.Link==link)
        .first())
    link.Scrape_Status = new_status
    db.session.commit()
    