from selenium.webdriver import Firefox, Chrome, Safari, Edge
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions


def pick_selenium_driver(browser_type="firefox", headless=False) -> WebDriver:
    # TODO abiliy to pass options that will be utilized in driver
    browser_type = browser_type.lower()
    accepted_drivers = {
        "firefox":Firefox,
        "chrome":Chrome,
        "safari":Safari,
        "edge":Edge}
    accepted_options = {
        "firefox":FirefoxOptions,
        "chrome":Chrome,
        "safari":Safari,
        "edge":Edge}
    
    try:
        selected_options = accepted_options[browser_type]()
        selected_options.headless = headless
        selected_driver =  accepted_drivers[browser_type](options=selected_options)
        return selected_driver
    except TypeError:
        return None