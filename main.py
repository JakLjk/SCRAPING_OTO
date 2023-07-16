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

    # scrape_init(scrape_type="links")
    
    scrape_init(scrape_type="offers")

if __name__=="__main__":
    main()



