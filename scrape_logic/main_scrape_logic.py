from sqlalchemy import Engine

from .offer_links_scraper.scrape_links_logic import scrape_links


def scrape_init(scrape_type:str):
    """Functions that allows for choosing which process should be initialized"""
    scrape_type = scrape_type.lower()
    if scrape_type == "links":
        scrape_links()
    elif scrape_type == "offers":
        pass
    else:
        raise ValueError("Wrong string value argument passed in scrape_type should pass: [links] or [offers]")
