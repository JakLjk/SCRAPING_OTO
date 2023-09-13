from logger import logger

from config import Config

from response_methods import selenium_get_retry
from response_methods import pick_selenium_driver

from db import engine, links_table, raw_offer_data_table
from sqlalchemy.orm import Session
from sqlalchemy.sql import or_
from sqlalchemy import select, exists, insert

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException, ElementClickInterceptedException, NoSuchElementException

from time import sleep, time, strftime, gmtime
from datetime import datetime

import bs4

from client_access_methods.get_link import get_link, change_link_status, update_error_message
from client_access_methods.post_raw_page_data import post_raw_data
from config import OperationTypes, DBTableConfig

# from dummy import get_link, change_link_status, update_error_message,post_raw_data

def scrape_offer():
    # Wait time for new link to scrape, if there are no links to scrape available
    wait_for_link_to_scrape = Config.OffersScrapingSetup.WAIT_TIME_FOR_NEW_LINKS_TO_SCRAPE
    wait_time_after_improper_page_load = Config.OffersScrapingSetup.WAIT_TIME_AFTER_IMPROPER_PAGE_LOAD
    max_concurrent_repeats = Config.OffersScrapingSetup.NUM_OF_MAX_SCRAPE_RETRIES


    logger.info("Initializing offer data scraping process.")
    # Setting up variables which will give information about amount of
    # time the function was running and number of pages that were being worked on.
    num_of_pages_parsed = 0
    main_scrape_begin_time = time()
    concurrent_load_title_errors = 0

    while True:
        try:
            logger.info('=================================================')
            current_iteration_begin_time = time()
            num_of_pages_parsed += 1

            logger.info(f"Fetching link to scrape from db...")

            # get link which was not scraped earlier, is not already scraped
            link_data = get_link()
            status = link_data["Status"]
            link = link_data["Link"]
            if not status == OperationTypes.status_success:
                    logger.info(f"There was an issue with fetching link from db. Getting different link in {wait_for_link_to_scrape} seconds.")
                    update_error_message(link, f"There was an issue with fetching link from db. Getting different link in {wait_for_link_to_scrape} seconds.")
                    change_link_status(link, DBTableConfig.links_table_scrape_status_error)
                    sleep(wait_for_link_to_scrape)
                    continue
            
            logger.info(f"Link selected: {link}")

            page_html = None

            # try:
            #     page_html, webpage_style = init_driver_scrape_process(link)
            # except AttributeError as ae:
            #     if concurrent_load_title_errors >= max_concurrent_repeats:
            #         logger.info(f"Max retries amount exceeded, marking link as broken")
            #         update_error_message(link, str(ae))
            #         change_link_status(link, DBTableConfig.links_table_scrape_status_error)
            #         logger.info(f"Link marked as error: {link}")
            #         continue
            #     else:
            #         logger.info(f"Attribute error has appeared, resuming scraping process in {wait_time_after_improper_page_load} seconds")
            #         concurrent_load_title_errors += 1
            #         sleep(wait_time_after_improper_page_load)

            try:
                page_html, webpage_style = init_driver_scrape_process(link)
            except AttributeError as ae:
                update_error_message(link, str(ae))
                change_link_status(link, DBTableConfig.links_table_scrape_status_error)
                logger.info(f"Link marked as error: {link}")
                continue
            except NoSuchElementException as nsee:
                update_error_message(link, str(nsee))
                change_link_status(link, DBTableConfig.links_table_scrape_status_error)
                logger.info(f"Link marked as error: {link}")
                continue

            # concurrent_load_title_errors = 0

            if page_html is None:
                    logger.error("Received empty from scrape function, skipping...")
                    update_error_message(link, "Received empty from scrape function, skipping...")
                    change_link_status(link, DBTableConfig.links_table_scrape_status_error)
                    continue

            logger.info(f"Inserting offer raw data into db.")
            post_raw_data(raw_data=page_html,
                          webpage_stype = webpage_style,
                            used_link=link)

            logger.info(f"Updating 'Scrape_Staus' in links table to {DBTableConfig.links_table_scrape_status_scraped}")
            
            change_link_status(link, DBTableConfig.links_table_scrape_status_scraped )
            this_iter_time = strftime('%M:%S', gmtime(time() - current_iteration_begin_time))
            whole_process_time = strftime('%H:%M:%S', gmtime(time() - main_scrape_begin_time))
            logger.info(f"Current iteration took {this_iter_time}. Whole process is taking: {whole_process_time}.")
        except Exception as ex:
            update_error_message(link, str(ex))
            change_link_status(link, DBTableConfig.links_table_scrape_status_error)
            raise ex 
             
             

def init_driver_scrape_process(link):
    """Returns None in case of error"""
    num_of_retries = Config.OffersScrapingSetup.NUM_OF_MAX_SCRAPE_RETRIES
    max_delay_when_waiting_for_element_load = Config.OffersScrapingSetup.MAX_TIME_WHEN_WAITING_FOR_ELEM_LOAD
    interval_between_retries = Config.OffersScrapingSetup.INTERVAL_BETWEEN_RETRIES
    technical_sleep_time_between_driver_script_exec = Config.OffersScrapingSetup.TECHNICAL_TIME_SLEEP_DRIVER_SCRIPT_EXEC
    driver_type = Config.SeleniumDriverSetup.DRIVER_TYPE
    run_headless = Config.SeleniumDriverSetup.DRIVER_HEADLESS


    logger.info(f"---Initializing selenium webdriver---")
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
    driver.execute_script("window.scrollTo(0,3600)")
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
    

    webpage_style = None

    logger.info("Ascertaining that webpage was loaded properly and discovering webpage layout [legacy/new]")
    try: 
        driver.find_element(By.CSS_SELECTOR, "h1.offer-title.big-text")
        webpage_style = "OLD"
    except:
        try:
            driver.find_element(By.CSS_SELECTOR, "h3.offer-title.big-text")
            webpage_style = "NEW"

        except NoSuchElementException as nsee:
             logger.error("Could not locate the title which is used to ascert that webpage was loaded properly")
             driver.quit()
             raise NoSuchElementException
        
    assert webpage_style, "Problem with generating "


    logger.info(f"Closing driver session.")
    page_html = driver.page_source
    driver.quit()
    logger.info("Driver session closed")


    driver.quit()
    return page_html, webpage_style