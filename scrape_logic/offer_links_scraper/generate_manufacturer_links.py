
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from time import sleep
from unidecode import unidecode

import bs4

from logger import logger
from config import Config

from response_methods import pick_selenium_driver

def generate_separate_manufacturer_links():
    """Generates list of links that are separated based on manufacturer name,
    and if number of availabe offers is greater than specified number,
    it will also separate them by voivodeships"""

    # Load necessarry configs
    run_headless = Config.SeleniumDriverSetup.DRIVER_HEADLESS
    browser_type = Config.SeleniumDriverSetup.DRIVER_TYPE
    max_delay_when_waiting_for_element_load = Config.LinksScrapingSetup.MAX_TIME_WHEN_WAITING_FOR_ELEM_LOAD
    technical_script_wait_time = Config.LinksScrapingSetup.TECHNICAL_SCRIPT_WAIT_TIME

    run_headless = Config.SeleniumDriverSetup.DRIVER_HEADLESS
    browser_type = Config.SeleniumDriverSetup.DRIVER_TYPE

    main_page_link = Config.LinksSetup.MAIN_PAGE_LINK
    template_link = Config.LinksSetup.TEMPLATE_LINK
    template_link_voivodeship = Config.LinksSetup.TEMPLATE_LINK_VOIVODESHIP
    template_link_page_num = Config.LinksSetup.TEMPLATE_LINK_PAGE_NUM

    max_num_offers_to_skip_voivdeship_split = Config.LinksSetup.MAX_NUM_OFFERS_ON_MANU_WITHOUT_SPLIT
    voivodeship_names = Config.LinksSetup.VOIVODESHIPS
    unwanted_manufacturer_names = Config.LinksSetup.UNWANTED_MANUFACTURER_NAMES
    replace_manufacturer_names = Config.LinksSetup.REPLACE_MANUFACTURER_NAMES
    replace_manufacturer_names_keys = replace_manufacturer_names.keys()

    # Selects only the voivodeships that are to be included in scraping process,
    # Based on bool value provided in config
    accepted_voivodeships = [voi_name for voi_name,
                            accepted in voivodeship_names.items()
                            if accepted]
    accepted_voivodeships_log_string = ', '.join(accepted_voivodeships)
    logger.info("Generating separate manufacturer links")
    logger.info(f"Voivodeships taken into account: {accepted_voivodeships_log_string}")
    logger.info("Initializing webdriver")
    driver = pick_selenium_driver(browser_type=browser_type, 
                                  headless=run_headless)
    
    logger.info(f"Loading url: {main_page_link}")
    driver.get(url=main_page_link)
    
    # Try to close cookie button, if such is to appear
    logger.info(f"Trying to close cookies popup...")
    try:    
        cookie_button = (WebDriverWait(driver, max_delay_when_waiting_for_element_load)
                    .until(EC.presence_of_element_located((By.ID, 'onetrust-accept-btn-handler'))))
        cookie_button.click()
        logger.info("Cookies popup was closed.")
    except TimeoutException:
            logger.info("Cookie popup wasn't closed (It is possible that it has not shown)")
            logger.info(f"Link: {main_page_link}") 

    logger.info(f"Searching for manufacturer names list button")
    sleep(technical_script_wait_time)
    car_models_button =  driver.find_element(By.XPATH,
    "/html/body/div[1]/div/div/div/main/div[2]/article/fieldset/div/form/div[1]/div[2]/div/div/div/button")
    logger.info("Clicking button to unfold data about unique car manufacturers...")
    car_models_button.click()
    page_html = driver.page_source
    driver.quit()
    soup = bs4.BeautifulSoup(page_html, 'html.parser')

    logger.info("Scraping unique car producer names")
    all_car_producents = soup.find_all("span", {"class":"ooa-micpln er34gjf0"})
    all_links = []
    for manufacturer_name in all_car_producents:
        name_info = manufacturer_name.getText().split("(")
        name = str(name_info[0]).strip()
        name = unidecode(name)
        name = name.replace(" ", "-")
        # Check if scraped string with manufacturer name is not to be excluded
        # Or altered based on information provided in config
        if name not in unwanted_manufacturer_names:
            if name in replace_manufacturer_names_keys:
                 name = replace_manufacturer_names[name]
            num_offers = int(name_info[1].replace(")", ""))
            if num_offers != 0:
                # If number of offers on specific manufacturer is higher that value specified
                # in config, there's need to separate manufacturer into voicodeships
                # Since otomoto allows to scroll back max to 500 page   
                template_link_with_voivodeship = \
                    template_link+template_link_voivodeship
                template_links_with_voivodeships = \
                    [template_link_with_voivodeship
                    .format(name, voivodeship)
                    for voivodeship in accepted_voivodeships]
                all_links.extend(template_links_with_voivodeships)
    logger.info(f"Returning unique manufacturer links")
    return all_links


