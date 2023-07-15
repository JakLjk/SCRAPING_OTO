# TODO DB lock logic - for blocking link when one of machines is working on it 
from logger import logger


from db import engine, links_table
from sqlalchemy.orm import Session
from sqlalchemy import select

def scrape_offer():
    num_of_reties = None
    interval_between_retries = None
    driver_type = None 

    logger.info("Initializing offer data scraping process.")
    # TODO select first row that was not yet scraped
    # TODO put lock on it and change status 
    # TODO After successfull ofeer data scrape put proper status
    # TODO if scrape failed put proper status
    # with engine.connect() as conn:
    #     with conn.begin() as trans:
    #         link = trans.query
        # conn.execute()

    with Session(engine) as session:
        link = (session.query(links_table)
                        # .order_by(links_table.c.Scrape_Date.desc())
                        # .with_for_update()

                        .with_for_update(skip_locked=True)
                       .first()

                        )
        # TODO add offer scraping logic whilst session is running

        # statement = select(link.Link)
        # x = session.execute(statement)
        # print(x)

        session.commit()
        print(link)
        
        # statement = select(link.Link)
        # x = session.execute(statement)
        # print(x)

        # statement = select(links_table).filter_by(ID_L=2)
        # link_row = session.scalars(statement).all()
        # statement = select(links_table.c.Link)
        # x = session.execute(statement).all()

