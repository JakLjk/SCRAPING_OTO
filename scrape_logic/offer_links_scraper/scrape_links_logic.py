from logger import logger
from config import Config

from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from response_methods import selenium_get_retry
from response_methods import pick_selenium_driver
from .num_pages import get_num_pages

import bs4

from datetime import datetime

from sqlalchemy import insert, func
from sqlalchemy.orm import Session

from db import engine, links_table


def scrape_links():
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
    num_of_pages_parsed = 0
    number_of_subsequent_fetch_link_failures = 0
    number_of_subsequent_0_links_passed_error = 0
    for page_link in separate_page_links:
        num_of_pages_parsed += 1 
        logger.info("===============================")
        logger.info(f"Parsing page {num_of_pages_parsed} / {num_pages}")
        logger.info(f"Fetching page data for link: {page_link}")
        driver = pick_selenium_driver(driver_type, run_headless)
        try:
            selenium_get_retry(driver=driver, link=page_link, 
                                            num_retries=num_of_retries, 
                                            retry_intervals_seconds=interval_between_retries)
            number_of_subsequent_fetch_link_failures = 0
        except WebDriverException as wde:
            logger.error(f"Fetching data for link failed: {page_link}. Continuing with next link.")
            number_of_subsequent_fetch_link_failures += 1
            if number_of_subsequent_fetch_link_failures > max_accepted_subsequent_failed_link_scrape_failures:
                raise WebDriverException(f"Fetching link failed {number_of_subsequent_fetch_link_failures} times, \
                                          which is max value of failures specified in config.")
            continue

        logger.info(f"Waiting for 'Accept Cookies' popup to appear...")
        # Try to close cookie button, if such is to appear
        try:    
            cookie_button = (WebDriverWait(driver, max_delay_when_waiting_for_element_load)
                        .until(EC.presence_of_element_located((By.ID, 'onetrust-accept-btn-handler'))))
            cookie_button.click()
            logger.info("Cookies popup was closed.")
        except TimeoutException:
                logger.info("Cookie popup wasn't closed (It is possible that it has not shown)")
                logger.info(f"Link: {page_link}") 
        page_html = driver.page_source


        # print(page_html)
        from time import sleep
        # sleep(1000)


        driver.close()

        # Filter all links on current page
        soup = bs4.BeautifulSoup(page_html, 'html.parser')
        try:
            elements_no_promo = soup.find('main',  
                {"class":"ooa-1hab6wx er8sc6m9"})
            all_link_elems = elements_no_promo.find_all("h2",
                {"class":"evg565y7 evg565y23 ooa-10p8u4x er34gjf0"})
        except AttributeError as ae:
            logger.error(ae)
            logger.error(f"Unable to properly scrape page: {page_link}.")
            logger.error("If error persists, it's possible that website structure has changed")
            logger.error("Proceeding to the next page link.")
            continue
        all_links = [elem.find("a")['href'] for elem in all_link_elems]


        if all_links == 0:
            if number_of_subsequent_0_links_passed_error > max_accepted_subsequent_failed_0_links_scraped_failures:
                raise AttributeError(f"Number of subsequent scraping iterations that return 0 links is higher than \
                                     {number_of_subsequent_0_links_passed_error}, which is max number specified in config")
        number_of_subsequent_0_links_passed_error = 0
    

        with Session(engine) as session: 
            # Check if lin already in db, to see if there's need to pass it again
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
    exists = live_session.query(links_table.c.Link==link).count()
    return bool(exists)
