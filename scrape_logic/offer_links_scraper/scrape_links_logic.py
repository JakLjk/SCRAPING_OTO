from logger import logger
from config import Config
from selenium.common.exceptions import WebDriverException


from response_methods import selenium_get_retry
from response_methods import pick_selenium_driver
from .num_pages import get_num_pages

import bs4

from datetime import datetime

from sqlalchemy import insert, func
from db import engine, links_table



def scrape_links():
    num_of_retries = Config.LinksScrapingSetup.NUMBER_OF_RETRIES_FOR_EACH_LINKS_PAGE
    interval_between_retries = Config.LinksScrapingSetup.SLEEP_SECONDS_BETWEEN_RETIRES
    driver_type = Config.SeleniumDriverSetup.DRIVER_TYPE
    # TODO add variable do config
    run_headless = True

    logger.info("Initializing links scraping process.")
    logger.info("Fetching number of pages to parse.")
    num_pages = get_num_pages()
    logger.info(f"There are {num_pages} pages to parse.")
    logger.info(f"Generating dummy link for every page with offer links...")
    # List of links that have to be loaded in order to fetch information about all offers
    # Links are in reverse order, to fetch the last offers that are listed as first, which reduces
    # Problems with last page index moving forwards or backwards
    separate_page_links = (Config.LinksSetup.OFFER_SCROLL_LIST_PAGE_LINK_PARSED.format(i)
                            for i in range(num_pages, 0, -1))
    logger.info(f"Generated {num_pages} dummy page links")
    # Allows for tracking subsequent failuers in scraping proces, in order to
    # break from look if the whole scraping process does not get response for subsequenst amount
    # of retries
    number_of_subsequent_failures = 0
    for page_link in separate_page_links:
        logger.info(f"Fetching page data for link: {page_link}")
        driver = pick_selenium_driver(driver_type, run_headless)
        try:
            selenium_get_retry(driver=driver, link=page_link, 
                                            num_retries=num_of_retries, 
                                            retry_intervals_seconds=interval_between_retries)
        except WebDriverException as wde:
            logger.error(f"Fetching data for link failed: {page_link}. Continuing with next link.")
            number_of_subsequent_failures += 1
            continue
        page_html = driver.page_source
        driver.close()

        # TODO implement configurable by config break of function if
        # there are subsequent failed responses
        # if number_of_subsequent_failures > x ...

        # Filter all links on current page
        soup = bs4.BeautifulSoup(page_html, 'html.parser')
        number_of_subsequent_failures = 0   
        try:
            elements_no_promo = soup.find('main',  
                {"class":"ooa-1hab6wx er8sc6m9"})
            all_link_elems = elements_no_promo.find_all("h1",
                {"class":"ev7e6t89 ooa-1xvnx1e er34gjf0"})
        except AttributeError as ae:
            logger.error(ae)
            logger.error(f"Unable to properly scrape page: {page_link}.")
            logger.error("If error persists, it's possible that website structure has changed")
            logger.error("Proceeding to the next link.")
            continue
        all_links = [elem.find("a")['href'] for elem in all_link_elems]
        
        #Put all links into database
        curr_date = datetime.today().strftime('%Y-%m-%d')
        statement = insert(links_table)
        link_rows_to_pass_to_db = [{"Scrape_Date":curr_date,
                                    "Link":link, 
                                    "Scrape_Status":"Not_Scraped"} 
                                    for link in all_links]
        logger.info(f"Passing {len(link_rows_to_pass_to_db)} to database.")
        with engine.connect() as conn:
            conn.execute(statement,link_rows_to_pass_to_db)
            conn.commit()
            logger.info("Connection executed, links passed")
            # TODO Return last insert and count inserted columns, to see if all were passed
            # last_return = insert(links_table).returning(
            #     links_table.c.Link)
            # print(last_return)
