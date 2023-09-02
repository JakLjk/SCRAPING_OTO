class ServConfig:
    DB_USERNAME = "dummy"
    DB_PASSWORD = ""
    DB_HOST = ""
    DATABASE_NAME = "otomoto"

    secret_Key = ""

    server_address = "http://192.168.0.88:5000"
    webhook_subdirectory = "/data-hook"

    full_webhook_path = server_address + webhook_subdirectory

class DBTableConfig:
    links_table_scrape_status_not_scraped = "NOT_SCRAPED"
    links_table_scrape_status_being_scraped = "IN_SCRAPING"
    links_table_link_health_healthy = "HEALTHY"

class OperationTypes:
    link_to_db = "LINK_TO_DB"
    link_from_db = "LINK_FROM_DB"

    status_success = "SUCCESS"
    status_failed = "FAILED"