class ServConfig:
    DB_USERNAME = "dummy"
    DB_PASSWORD = "dummy"
    DB_HOST = ""
    DATABASE_NAME = "otomoto"

    secret_Key = ""

    server_address = "http://192.168.0.88:5000"
    webhook_subdirectory = "/data-hook"

    full_webhook_path = server_address + webhook_subdirectory

class DBTableConfig:
    links_table_scrape_status_not_scraped = "NOT_SCRAPED"
    links_table_scrape_status_being_scraped = "IN_SCRAPING"
    links_table_scrape_status_scraped = "WAS_SCRAPED"
    links_table_scrape_status_error = "ERROR"

    raw_data_table_etl_not_performed = "NOT_PERFORMED"
    raw_data_table_etl_performed = "PERFORMED"

class OperationTypes:
    link_to_db = "LINK_TO_DB"
    link_from_db = "LINK_FROM_DB"
    update_link_status = "UPDATE_LINK_STATUS"
    update_link_health_status = "UPDATE_LINK_HEALTH_STATUS"
    raw_data_to_db = "RAW_TO_DB"
    get_raw_data = "GET_RAW_DATA"
    update_etl_status = "UPDATE_ETL"
    push_offer_details_to_db = "PUSH_DETAILS_TO_DB"
    get_row_data_for_helper_table = "GET_DATA_FOR_HELPER_TABLE"
    get_currently_available_column_names = "GET_AVAILABLE_COLUMN_NAMES"
    add_column_to_table = "ADD_COLUMN"
    insert_data_into_helper_table = "ADD_DATA+TO_HELPER"
    update_error_message = "UPDATE_ERROR_MESSAGE"
 
    status_success = "SUCCESS"
    status_failed = "FAILED"

    link_scrape_status_scraped = "SCRAPED"

    link_health_status_good = "GOOD"
    link_health_status_broken = "BROKEN"

