from selenium.webdriver import Firefox, Chrome, Safari, Edge

def pick_selenium_driver(browser_type="firefox"):
    browser_type = browser_type.lower()
    accepted_drivers = {
        "firefox":Firefox,
        "chrome":Chrome,
        "safari":Safari,
        "edge":Edge}
    try:
        return accepted_drivers[browser_type]
    except TypeError:
        return None