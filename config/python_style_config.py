class Config:

    TEST = "TEST"

    # Selenium driver setup
    DRIVER_HEADLESS = True
    DRIVER_TYPE = "firefox"

    # Links setup
    FIRST_OFFER_PAGE_SCROLL_LINK = "https://www.otomoto.pl/osobowe"
    OFFER_SCROLL_LIST_PAGE_LINK_PARSED = "https://www.otomoto.pl/osobowe?page={}"
    
    # Logging setup
    LOG_FILE_PATH_NAME=None