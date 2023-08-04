from logger import logger
from config import Config

from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from response_methods import selenium_get_retry
from response_methods import pick_selenium_driver

import bs4

from datetime import datetime

from sqlalchemy import insert, func
from sqlalchemy.orm import Session

from db import engine, links_table

from .get_num_pages import get_num_pages
from .generate_manufacturer_links import generate_separate_manufacturer_links


driver_type = Config.SeleniumDriverSetup.DRIVER_TYPE
run_headless = Config.SeleniumDriverSetup.DRIVER_HEADLESS
num_of_retries = Config.LinksScrapingSetup.NUMBER_OF_RETRIES_FOR_EACH_LINKS_PAGE
interval_between_retries = Config.LinksScrapingSetup.SLEEP_SECONDS_BETWEEN_RETIRES
scrape_existing = Config.LinksScrapingSetup.SCRAPE_EXISTING_IN_DB
max_delay_when_waiting_for_element_load = \
    Config.LinksScrapingSetup.MAX_TIME_WHEN_WAITING_FOR_ELEM_LOAD
max_accepted_subsequent_failed_link_scrape_failures = \
    Config.LinksScrapingSetup.MAX_ACCEPTED_SUBSEQUENT_FAILED_LINK_SCRAPE_FAILURES
max_accepted_subsequent_failed_0_links_scraped_failures = \
    Config.LinksScrapingSetup.MAX_ACCEPTED_SUBSEQUENT_FAILED_0_LINKS_FAILURES
template_link_page_num = Config.LinksSetup.TEMPLATE_LINK_PAGE_NUM


def scrape_links():
    """Main scraping function managing process from generating links to sending
    data to database"""
    logger.info("Initializing links scraping process.")
    logger.info(f"Generating dummy link for every page with offer links...")

    dummy_links = generate_separate_manufacturer_links()

    # Keep count of subsequent faliures
    subsequent_failures = 0
    for dummy_link_first_pages in dummy_links:
        # Get number of pages based on first page link specified for manufacturer
        number_of_pages_to_parse = get_num_pages(dummy_link_first_pages)
        logger.info(f"Parsing link: {dummy_link_first_pages}")
        # scrape data for first link
        if scrape_links_for_link_specified(link=dummy_link_first_pages):
            logger.info(f"Scrape for {dummy_link_first_pages} has finished successfully.")
        else:
            logger.info(f"Scrape for {dummy_link_first_pages} has encountered a problem.")
        # In case of situation, where there is more than one page provided for manufacturer,
        # generate link for each page and scrape links on each of them
        if number_of_pages_to_parse is not None:
            for page_num in range(2, number_of_pages_to_parse):
                logger.info("================================================")
                dummy_link_with_page_info = dummy_link_first_pages + \
                    template_link_page_num
                current_page_link = dummy_link_with_page_info.format(page_num)
                logger.info(f"Parsing link: {current_page_link}")
                if scrape_links_for_link_specified(link=current_page_link):
                    logger.info(f"Scrape for {current_page_link} has finished successfully.")
                    subsequent_failures = 0
                else:
                    logger.info(f"Scrape for {current_page_link} has encountered a problem.")
                    subsequent_failures += 1
                    assert_subsequent_failures(subsequent_failures)


def scrape_links_for_link_specified(link):
        logger.info(f"Scraping page html...")
        page_html = get_page_raw_source(link)
        if page_html is None:
            return False
        logger.info(f"Parsing page html into links... ")
        page_links = get_offer_links_from_curr_page(page_html)
        # TODO add timeout mechanism as in page html scraping
        if page_links is None: return False
        logger.info(f"Passing liks to db...")
        commit_links_to_db(page_links)
        return True


def get_page_raw_source(current_page_link:str):
    driver = pick_selenium_driver(driver_type, run_headless)
    try:
        selenium_get_retry(driver=driver, link=current_page_link, 
                                        num_retries=num_of_retries, 
                                        retry_intervals_seconds=interval_between_retries)
    except WebDriverException as wde: 
        logger.info("WebDriverException was raised whilst trying to load webpage")
        driver.quit()
        return None
    logger.info(f"Waiting for 'Accept Cookies' popup to appear...")
    # Try to close cookie button, if such is to appear
    try:    
        cookie_button = (WebDriverWait(driver, max_delay_when_waiting_for_element_load)
                    .until(EC.presence_of_element_located((By.ID, 'onetrust-accept-btn-handler'))))
        cookie_button.click()
        logger.info("Cookies popup was closed.")
    except TimeoutException:
            logger.info("Cookie popup wasn't closed (It is possible that it has not shown)")
    page_html = driver.page_source
    driver.quit()
    return page_html


def get_offer_links_from_curr_page(page_html):
    soup = bs4.BeautifulSoup(page_html, 'html.parser')
    try:
        elements_no_promo = soup.find('main',  
            {"class":"ooa-1hab6wx er8sc6m9"})
        all_link_elems = elements_no_promo.find_all("h2",
            {"class":"evg565y7 evg565y23 ooa-10p8u4x er34gjf0"})
    except AttributeError as ae:
        logger.error(ae)
        # logger.error(f"Unable to properly scrape page: {page_link}.")
        logger.error("If error persists, it's possible that website structure has changed")
        logger.error("Proceeding to the next page link.")
        return None
    return [elem.find("a")['href'] for elem in all_link_elems]


def commit_links_to_db(all_links):
    with Session(engine) as session: 
    # Check if link already in db, to see if there's need to pass it again
        if not scrape_existing:
            all_links = [link for link in all_links if not link_exists(link, session)]
        #Put all links into database
        curr_date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        statement = insert(links_table)
        link_rows_to_pass_to_db = [{"Scrape_DateTime":curr_date,
                                    "Link":link, 
                                    "Scrape_Status":"Not_Scraped"} 
                                    for link in all_links]
        logger.info(f"Passing {len(link_rows_to_pass_to_db)} links to database.")
        session.execute(statement,link_rows_to_pass_to_db)
        session.commit()
        rows_left = (session.query(links_table)
            .filter(links_table.c.Scrape_Status=="Not_Scraped")
            .distinct(links_table.c.Link)
            .count())
        logger.info(f"There are currently {rows_left} links to be scraped in database.")


def link_exists(link:str, live_session:Session) -> bool:
    exists = live_session.query(links_table).filter(links_table.c.Link==link).count()
    return bool(exists)


def assert_subsequent_failures(subsequent_failures):
    if subsequent_failures > max_accepted_subsequent_failed_link_scrape_failures:
        raise WebDriverException(f"Fetching link failed {subsequent_failures} times, \
                        which is max value of failures specified in config.")
