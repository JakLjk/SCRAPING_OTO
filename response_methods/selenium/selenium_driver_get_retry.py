from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import WebDriverException
from time import sleep

from logger import logger

def selenium_get_retry(driver:WebDriver, 
                       link:str, 
                       num_retries:int, 
                       retry_intervals_seconds=2):
    """Allows user to retry get functions everal times.
    user can specify time betweeen each retry
    After failing designeated number of times, will return None"""

    retries = 0
    while retries <= num_retries:
        sleep(retry_intervals_seconds)
        try:
            driver.get(link)
            break
        except WebDriverException as wde:
            retries += 1
            logger.warning(f"Failed to reach webpage: {link}")
            if not retries <= num_retries:
                logger.warning(f"All {num_retries} retries failed - no website data retreived")
                raise WebDriverException(f"Could not fetch website data afrer {num_retries} retires")
            else:
                logger.warning(f"Website fetch failed - retrying. (retry {retries}/{num_retries})")
