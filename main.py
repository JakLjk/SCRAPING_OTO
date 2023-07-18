import os, sys

from scrape_logic import scrape_init
from logger import logger

# Adding necessary paths into PATH for the time of session run
# TODO alter path so it'll work for all dirs
sys.path.append("/Users/jakub/VS_Projects/SCRAPING_OTO/response_methods")

def main():
    # TODO add scrape Time column 
    # scrape_init(scrape_type="links")

    # TODO change DATE to DATETIME
    scrape_init(scrape_type="offers")



if __name__=="__main__":
    main()



