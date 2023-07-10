from logger import logger
from config import Config

from response_methods import selenium_get_retry
from response_methods import pick_selenium_driver
from .num_pages import get_num_pages

from selenium.common.exceptions import WebDriverException
from sqlalchemy import Engine

def scrape_links(db_engine:Engine):
    num_of_retries = Config.LinksScrapingSetup.NUMBER_OF_RETRIES_FOR_EACH_LINKS_PAGE
    interval_between_retries = Config.LinksScrapingSetup.SLEEP_SECONDS_BETWEEN_RETIRES
    driver_type = Config.SeleniumDriverSetup.DRIVER_TYPE

    logger.info("")

    logger.info("Beggining scraping of links.")
    logger.info("Fetching number of pages to parse.")
    num_pages = get_num_pages()
    logger.info(f"There are {num_pages} pages to parse.")
    logger.info(f"Generating link for every page with offer links")
    # List of links that have to be loaded in order to fetch information about all offers
    # Links are in reverse order, to fetch the last offers that are listed as first, which reduces
    # Problems with last page index moving forwards or backwards
    separate_page_links = (Config.LinksSetup.OFFER_SCROLL_LIST_PAGE_LINK_PARSED.format(i)
                            for i in range(num_pages, 0, -1))
    logger.info(f"Generated {num_pages} links")

    # Allows for tracking subsequent failuers in scraping proces, in order to
    # break from look if the whole scraping process does not get response for subsequenst amount
    # of retries
    number_of_subsequent_failures = 0
    for page_link in separate_page_links:
        logger.info(f"Fetching page data for link: {page_link}")
        driver = pick_selenium_driver(driver_type, True)
        try:
            selenium_get_retry(driver=driver, link=page_link, 
                                            num_retries=num_of_retries, 
                                            retry_intervals_seconds=interval_between_retries)
        except WebDriverException as wde:
            logger.error(f"Fetching data for link failed: {page_link}. Continuing with next link.")
            number_of_subsequent_failures += 1
            continue
        # TODO implement configurable by config break of function if
        # there are subsequent failed responses
        number_of_subsequent_failures = 0
        with db_engine.connect() as conn:
            # TODO use in-built sqlalchemy functions, not raw SQL
            conn.execute
