from logger import logger

from config import Config

from response_methods import selenium_get_retry
from response_methods import pick_selenium_driver

from db import engine, links_table, raw_offer_data_table
from sqlalchemy.orm import Session
from sqlalchemy import select, exists, insert

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException, ElementClickInterceptedException

from time import sleep, time, strftime, gmtime
from datetime import datetime


def scrape_offer():
    # Wait time for new link to scrape, if there are no links to scrape available
    wait_for_link_to_scrape = Config.OffersScrapingSetup.WAIT_TIME_FOR_NEW_LINKS_TO_SCRAPE

    logger.info("Initializing offer data scraping process.")
    # Setting up variables which will give information about amount of
    # time the function was running and number of pages that were being worked on.
    num_of_pages_parsed = 0
    main_scrape_begin_time = time()

    while True:
        logger.info('=================================================')
        current_iteration_begin_time = time()
        num_of_pages_parsed += 1

        with Session(engine) as session:
            # Link returns first row, which is not yet present in scraped data, and locks it for time of transaction
            # In order to prevent other scrapers scraping this function (to save resources)
            rows_left = (session.query(links_table)
                    .filter(links_table.c.Scrape_Status=="Not_Scraped")
                    .distinct(links_table.c.Link)
                    .count())
            
            logger.info(f"Scraping iteration number {num_of_pages_parsed}. There are {rows_left} links to be scraped left.")
            logger.info(f"Fetching link to scrape from db...")

            link_row = (session.query(links_table)
                            .filter(links_table.c.Scrape_Status=="Not_Scraped")
                            .filter(~ exists().where(links_table.c.Link==raw_offer_data_table.c.Used_Link))
                            .with_for_update(skip_locked=True)
                            .first())
            
            if link_row == None:
                  logger.info(f"There are no links to scrape currently, checking again in {wait_for_link_to_scrape} seconds.")
                  sleep(wait_for_link_to_scrape)
                  continue
                
            link = link_row.Link
            logger.info(f"Link selected: {link}")

            page_html = init_driver_scrape_process(link)
            if page_html is None:
                  logger.error("Received empty from scrape function, skipping...")
                  continue

            logger.info(f"Inserting offer raw data into db.")
            # Insert data into offer raw table
            curr_date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
            statement = (insert(raw_offer_data_table)
                        .values(DATE=curr_date,
                            Raw_Data=page_html,
                            Used_Link=link))
            session.execute(statement)

            logger.info(f"Updating 'Scrape_Staus' in links table to 'Was_Scraped'")
            # Update links column Scrape_Status to Was_Scraped 
            num_rows_updated = (session.query(links_table)
                                .filter_by(Link=link)
                                .update(dict(Scrape_Status='Was_Scraped')))
            logger.info(f"Commiting changes to database...")
            session.commit()
            logger.info(f"Changes commited successfully.")
            this_iter_time = strftime('%M:%S', gmtime(time() - current_iteration_begin_time))
            whole_process_time = strftime('%H:%M:%S', gmtime(time() - main_scrape_begin_time))
            eta_time_left = strftime('%H:%M:%S', gmtime(current_iteration_begin_time*rows_left))
            logger.info(f"Current iteration took {this_iter_time}. Whole process is taking: {whole_process_time}.")
            logger.info(f"If this is the only process used, the ETA is approx. {eta_time_left}")


def init_driver_scrape_process(link):
    """Returns None in case of error"""
    num_of_retries = Config.OffersScrapingSetup.NUM_OF_MAX_SCRAPE_RETRIES
    max_delay_when_waiting_for_element_load = Config.OffersScrapingSetup.MAX_TIME_WHEN_WAITING_FOR_ELEM_LOAD
    interval_between_retries = Config.OffersScrapingSetup.INTERVAL_BETWEEN_RETRIES
    technical_sleep_time_between_driver_script_exec = Config.OffersScrapingSetup.TECHNICAL_TIME_SLEEP_DRIVER_SCRIPT_EXEC
    driver_type = Config.SeleniumDriverSetup.DRIVER_TYPE
    run_headless = Config.SeleniumDriverSetup.DRIVER_HEADLESS


    logger.info(f"Initializing selenium webdriver")
    driver = pick_selenium_driver(driver_type, run_headless)
    # Try to load offer page link
    try:
        selenium_get_retry(driver=driver, link=link, 
                                        num_retries=num_of_retries, 
                                        retry_intervals_seconds=interval_between_retries)
    except WebDriverException as wde:
        logger.error(f"Fetching data for link failed: {link}. Continuing with next link.")
        return None
    
    logger.info(f"Selenium driver initialized.")
    logger.info(f"Waiting for 'Accept Cookies' popup to appear...")
    # Try to close cookie button, if such is to appear
    try:    
        cookie_button = (WebDriverWait(driver, max_delay_when_waiting_for_element_load)
                    .until(EC.presence_of_element_located((By.ID, 'onetrust-accept-btn-handler'))))
        cookie_button.click()
        logger.info("Cookies popup was closed.")
    except TimeoutException:
            logger.info("Cookie popup wasn't closed (It is possible that it has not shown)")
            logger.info(f"Link: {link}") 

    # Scroll down in order to load dynamic JS and widgets, such as google map
    logger.info(f"Scrolling down through webpage to load additional widgets...")
    sleep(technical_sleep_time_between_driver_script_exec)
    driver.execute_script("window.scrollTo(0,2800)")
    sleep(technical_sleep_time_between_driver_script_exec)

    logger.info(f"Trying to expand additional offer information container.")
    # Try to expand section with additional information about offer
    equipment_expand_xpath = "/html/body/div[4]/main/div[1]/div[1]/div[2]/div[1]/div[1]/div[5]/a/i"
    try:
            expand_element_button = (WebDriverWait(driver, max_delay_when_waiting_for_element_load)
                                    .until(EC.visibility_of_element_located((By.XPATH, equipment_expand_xpath ))))
            expand_element_button.click()
            logger.info(f"Additional offer information container was expanded.")
    except TimeoutException:
            logger.error(f"Unable to expand vehicle equipment (most probably it is non-expandable).")
            logger.error(f"Link: {link}")
    except ElementClickInterceptedException as ecie:
            logger.error(f"Unable to expand vehicle equipment due to it being obscured. Maybe cookie popup was not closed properly?")
            logger.error(f"Link: {link}")
            logger.info(f"Closing driver session.")
            driver.quit()
            return None

    logger.info(f"Closing driver session.")
    page_html = driver.page_source
    driver.quit()

    return page_html