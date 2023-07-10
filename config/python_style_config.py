class Config:

    TEST = "TEST"

    class SeleniumDriverSetup:
        DRIVER_HEADLESS = True
        DRIVER_TYPE = "firefox"

    class LinksScrapingSetup:
        NUMBER_OF_RETRIES_FOR_EACH_LINKS_PAGE = 5
        SLEEP_SECONDS_BETWEEN_RETIRES = 1

    class LinksSetup:
        FIRST_OFFER_PAGE_SCROLL_LINK = "https://www.otomoto.pl/osobowe"
        OFFER_SCROLL_LIST_PAGE_LINK_PARSED = "https://www.otomoto.pl/osobowe?page={}"
    
    class LoggingSetup:
        LOG_FILE_PATH_NAME=None