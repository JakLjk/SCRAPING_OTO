from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from response_methods import pick_selenium_driver
from config import Config

from logger import logger

def get_num_pages(link: str):
    run_headless = Config.SeleniumDriverSetup.DRIVER_HEADLESS
    browser_type = Config.SeleniumDriverSetup.DRIVER_TYPE

    max_last_page_num = Config.LinksSetup.MAX_LAST_PAGE_NUM

    logger.info(f"Getting num of pages for link: {link}")

    driver = pick_selenium_driver(browser_type=browser_type, 
                                  headless=run_headless)
    
    driver.get(url=link)
    try:
        # last_page_num =  driver.find_element(By.XPATH,
        # "/html/body/div[1]/div/div/div/div[2]/div[2]/div[2]/div[1]/div[3]/div[3]/div/ul/li[6]/a/span").text
        last_page_num = driver.find_elements(By.CSS_SELECTOR, ".ooa-xdlax9.e1f09v7o0")
        if len(last_page_num) != 0:
            last_page_num = last_page_num[-1].text
        else:
            return None
    except NoSuchElementException as nsee:
        logger.info("Could not locate element with last page. Either there is no such element, or page layout has changed.")
        logger.info(f"Link: {link}")
        driver.quit()
        # Return none in there is no more than 1 page to scrape
        return None
    driver.quit()
    assert int(last_page_num) < max_last_page_num, f"Last page number scraped is higher than maximum number allowed by config [{last_page_num}]"
    logger.info(f"Num of pages for link {link}: \n [{last_page_num}]")
    return int(last_page_num)



