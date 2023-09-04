from .load_and_transform import load_raw_offer_data, scrape_data_from_raw, set_link_scrape_status_to_true, write_offer_data_to_db

from time import sleep

from logger import logger
from config import Config

wait_time_if_no_link_to_parse = Config.ETL.WAIT_IF_NO_OFFERS_TO_PARSE

from client_access_methods.raw_page_interpreter_client_methods import get_raw_data, push_offer_details_to_db, update_etl_status
from config import DBTableConfig
def get_structurized_data():
    logger.info("Starting raw data processing...")
    while True:
        logger.info("Fetching raw page data from db")
        # row_data = load_raw_offer_data()
        try:
            raw_data = get_raw_data()
        except ValueError as ve:
            logger.info(f"{ve}")
            logger.info(f"There are no links to parse, checking again in {wait_time_if_no_link_to_parse} seconds")
            sleep(wait_time_if_no_link_to_parse)
            continue

        link = raw_data["Link"]
        raw_data = raw_data["rawData"]

        logger.info(f"Processing raw data for link {link}")
        scraped_data = scrape_data_from_raw(link,raw_data)

        logger.info(f"Inserting processed data into db")
        # write_offer_data_to_db(link=link,
        #                         offer_title=scraped_data["offer_title"],
        #                         offer_price=scraped_data["price"],
        #                         offer_details=scraped_data["offer_details"],
        #                         offer_equipment_details=scraped_data["equipment"],
        #                         offer_coordinates=scraped_data["coordinates"])
        try:
            push_offer_details_to_db(link=link,
                                    offer_title=scraped_data["offer_title"],
                                    offer_price=scraped_data["price"],
                                    offer_details=scraped_data["offer_details"],
                                    offer_equipment_details=scraped_data["equipment"],
                                    offer_coordinates=scraped_data["coordinates"])
        except ValueError as ve:
            logger.warning(f"{ve}")
            update_etl_status(link, DBTableConfig.raw_data_table_etl_performed)
            continue
        logger.info(f"Processed data was inserted into db.")
        logger.info(f"Setting ETL processed status as True for link {link}")
        # set_link_scrape_status_to_true(link)
        update_etl_status(link, DBTableConfig.raw_data_table_etl_performed)
        logger.info(f"Process finished for link {link}")
        logger.info("++++++++++++++++++++++++++++++++++++++++++++")
