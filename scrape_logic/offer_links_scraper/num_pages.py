from selenium.webdriver.common.by import By

from response_methods import pick_selenium_driver
from config import Config

def get_num_pages():
    run_headless = Config.DRIVER_HEADLESS
    browser_type = Config.DRIVER_TYPE
    first_page_link = Config.FIRST_OFFER_PAGE_SCROLL_LINK


    driver = pick_selenium_driver(browser_type=browser_type, 
                                  headless=run_headless)
    driver.get(url=first_page_link)
    last_page_num =  driver.find_element(By.XPATH,
    "/html/body/div[1]/div/div/div/div[2]/div[2]/div[2]/div[1]/div[3]/div[3]/div/ul/li[6]/a/span").text
    driver.quit()
    return int(last_page_num)

