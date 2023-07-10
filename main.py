import os, sys
import sqlalchemy as db

from config import Config
from scrape_logic import scrape_init
from logger import logger

# Adding necessary paths into PATH for the time of session run
# TODO alter path so it'll work for all dirs
sys.path.append("/Users/jakub/VS_Projects/SCRAPING_OTO/response_methods")

def main():

    
    # Initialize db connection
    # Load db structure
    logger.info(f"Connecting to db.")
    db_username = "root"
    db_password = ""
    host = "localhost"
    database = ""
    engine = db.create_engine(f"mysql+mysqlconnector://{db_username}:{db_password}@{host}/{database}", echo=True)
    # trying connetion to db
    engine.connect()

    # TODO based on tutorial, set up thedb insertion properly


    # engine = ""
    scrape_init(db_engine=engine, scrape_type="links")


if __name__=="__main__":
    main()




