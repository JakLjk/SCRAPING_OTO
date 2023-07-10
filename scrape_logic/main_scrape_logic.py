from .offer_links_scraper.scrape_links_logic import scrape_links

def scrape_init(db_engine, scrape_type:str):
    """Choose which one of scrapes should be launched"""
    scrape_type = scrape_type.lower()
    if scrape_type == "links":
        scrape_links()
