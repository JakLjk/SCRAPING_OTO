class Config:
    
    class SeleniumDriverSetup:
        DRIVER_HEADLESS = True
        DRIVER_TYPE = "firefox"

    class LinksScrapingSetup:
        NUMBER_OF_RETRIES_FOR_EACH_LINKS_PAGE = 5
        SLEEP_SECONDS_BETWEEN_RETIRES = 1
        MAX_TIME_WHEN_WAITING_FOR_ELEM_LOAD = 3
        MAX_ACCEPTED_SUBSEQUENT_FAILED_LINK_SCRAPE_FAILURES = 3
        MAX_ACCEPTED_SUBSEQUENT_FAILED_0_LINKS_FAILURES = 3
        TECHNICAL_SCRIPT_WAIT_TIME = 1.5
        # Scraping existing links means, that links that were previosly scraped will be inserted into db again,
        # along the new links. This apporach means, that if an offer under this specific link was scraped in past,
        # it will be scraped again (Which might be important to track changes in time)
        SCRAPE_EXISTING_IN_DB = False

    class OffersScrapingSetup:
        # How frequently should script ping db to check if there are any 
        # links available
        WAIT_TIME_FOR_NEW_LINKS_TO_SCRAPE = 60
        NUM_OF_MAX_SCRAPE_RETRIES = 3
        MAX_TIME_WHEN_WAITING_FOR_ELEM_LOAD = 3
        INTERVAL_BETWEEN_RETRIES = 3
        TECHNICAL_TIME_SLEEP_DRIVER_SCRIPT_EXEC = 0.25

    class LinksSetup:
        MAIN_PAGE_LINK = "https://www.otomoto.pl"
        TEMPLATE_LINK = "https://www.otomoto.pl/osobowe/{}"
        TEMPLATE_LINK_VOIVODESHIP = "/{}"
        TEMPLATE_LINK_PAGE_NUM = "&page={}"

        VOIVODESHIPS = ["slaskie",
                        "dolnoslaskie",
                        "kujawsko-pomorskie",
                        "lubelskie",
                        "lodzkie",
                        "malopolskie",
                        "mazowieckie",
                        "opolskie",
                        "podkarpackie",
                        "podlaskie",
                        "pomorskie",
                        "swietokrzyskie",
                        "warminsko-mazurskie",
                        "wielkopolskie",
                        "zachodniopomorskie"]
        
        UNWANTED_MANUFACTURER_NAMES = ["Wybierz",
                                       "Popularne"]
        REPLACE_MANUFACTURER_NAMES = {"Warszawa":"marka_warszawa",
                                      "BMW-ALPINA":"alpina",
                                      "Zastava":"zastawa"}
        
        MAX_NUM_OFFERS_ON_MANU_WITHOUT_SPLIT = 15000
        MAX_LAST_PAGE_NUM = 500
        NUM_OFFERS_PER_PAGE = 32

    class LoggingSetup:
        LOG_FILE_PATH_NAME=None