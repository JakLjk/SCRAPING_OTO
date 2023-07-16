# TODO DB lock logic - for blocking link when one of machines is working on it 
from logger import logger

from response_methods import selenium_get_retry
from response_methods import pick_selenium_driver

from db import engine, links_table, raw_offer_data_table
from sqlalchemy.orm import Session
from sqlalchemy import select, exists, insert

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException, ElementClickInterceptedException


from time import sleep
from datetime import datetime

def scrape_offer():
    # TODO connect to config file
    num_of_reties = None
    interval_between_retries = None
    driver_type = "firefox" 
    run_headless = True
    max_delay_when_waiting_for_element_load = 3
    technical_sleep_time_between_driver_script_exec = 0.25
    scrape_previously_scraped = False
    num_of_retries = 3 
    interval_between_retries = 2

    logger.info("Initializing offer data scraping process.")
    # TODO select first row that was not yet scraped
    # TODO put lock on it and change status 
    # TODO After successfull ofeer data scrape put proper status
    # TODO if scrape failed put proper status
    with Session(engine) as session:
        # TODO add with True functionality which will stop process when all links were scraped
        # Link returns first row, which is not yet present in scraped data, and locks it for time of transaction
        # In order to prevent other scrapers scraping this funciton (to save resources)
        logger.info(f"Fetching link to scrape from db...")
        link_row = (session.query(links_table)
                        .filter(links_table.c.Scrape_Status=="Not_Scraped")
                        .filter(~ exists().where(links_table.c.Link==raw_offer_data_table.c.Used_Link))
                        .with_for_update(skip_locked=True)
                        .first())
        link = link_row.Link

        logger.info(f"Link selected: {link}")
        logger.info(f"Initializing selenium webdriver")
        driver = pick_selenium_driver(driver_type, run_headless)

        # Try to load offer page link
        try:
            selenium_get_retry(driver=driver, link=link, 
                                            num_retries=num_of_retries, 
                                            retry_intervals_seconds=interval_between_retries)
        except WebDriverException as wde:
            logger.error(f"Fetching data for link failed: {link}. Continuing with next link.")
            # number_of_subsequent_failures += 1
            # TODO implement continue within while True loop, 
            # continue to next link
            pass
        
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
        logger.info(f"Scrolling down though webpage to load additional widgets...")
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
                # TODO add while True continue to proceed to next link

        logger.info(f"Closing driver session.")
        page_html = driver.page_source
        driver.quit()

        logger.info(f"Inserting offer raw data into db.")
        # Insert data into offer raw table
        curr_date = datetime.today().strftime('%Y-%m-%d')
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
