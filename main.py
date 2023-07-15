import os, sys
from sqlalchemy import func, insert

from config import Config
from scrape_logic import scrape_init
from logger import logger

from db import engine, metadata_obj, links_table
# Adding necessary paths into PATH for the time of session run
# TODO alter path so it'll work for all dirs
sys.path.append("/Users/jakub/VS_Projects/SCRAPING_OTO/response_methods")

def main():
    # test_statement = insert(links_table).values(
    # Scrape_Date=func.current_date(),
    # Link="TESTX1XXD21",
    # Was_Scraped=True)

    # with engine.connect() as conn:
    #     conn.execute(test_statement)
    #     conn.commit()

    scrape_init(scrape_type="links")


if __name__=="__main__":
    main()



