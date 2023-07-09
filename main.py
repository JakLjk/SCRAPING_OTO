import os, sys

from config import Config
from scrape_logic import scrape_init

sys.path.append("/Users/jakub/VS_Projects/SCRAPING_OTO/response_methods")

def main():
    # Read Config Data - No need to since config is python class object

    # Load db structure
    # Initialize db connection

    # pass db connector to scrape logic
    # Initialize scrape logic
    scrape_init(db_connector=None, scrape_type="links")


if __name__=="__main__":
    main()




