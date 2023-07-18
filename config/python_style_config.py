class Config:

    TEST = "TEST"

    class SeleniumDriverSetup:
        DRIVER_HEADLESS = False
        DRIVER_TYPE = "firefox"

    class LinksScrapingSetup:
        NUMBER_OF_RETRIES_FOR_EACH_LINKS_PAGE = 5
        SLEEP_SECONDS_BETWEEN_RETIRES = 1

    class OffersScrapingSetup:
        # How frequently should script ping db to check if there are any 
        # links available
        WAIT_TIME_FOR_NEW_LINKS_TO_SCRAPE = 60
        NUM_OF_MAX_SCRAPE_RETRIES = 3
        MAX_TIME_WHEN_WAITING_FOR_ELEM_LOAD = 3
        INTERVAL_BETWEEN_RETRIES = 3
        TECHNICAL_TIME_SLEEP_DRIVER_SCRIPT_EXEC = 0.25


    class LinksSetup:
        FIRST_OFFER_PAGE_SCROLL_LINK = "https://www.otomoto.pl/osobowe/katowice"
        OFFER_SCROLL_LIST_PAGE_LINK_PARSED = "https://www.otomoto.pl/osobowe/katowice?page={}"
    
    class LoggingSetup:
        LOG_FILE_PATH_NAME=None