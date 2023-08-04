# TODO Load offer data from databas
# TODO Convert data into usefull format 
# TODO load into proper db table
from sqlalchemy.orm import Session
from sqlalchemy import exists, insert
from time import sleep

import bs4
import re

from config import Config
from db import engine, raw_offer_data_table, offers_parsed
from logger import logger

wait_if_no_offers_available = Config.ETL.WAIT_IF_NO_OFFERS_TO_PARSE

def load_raw_offer_data():
    with Session(engine) as session:
        raw_data_row = (session.query(raw_offer_data_table)
                    .filter(raw_offer_data_table.c.ETL_Performed_Status=="False")
                    .filter(~ exists().where(offers_parsed.c.Link==raw_offer_data_table.c.Used_Link))
                    .with_for_update(skip_locked=True)
                    .first())
        
        if raw_data_row is None:
               return None
        
        return {"link":raw_data_row.Link, "raw_data":raw_data_row.Raw_Data}
            


def scrape_data_from_raw(link:str, raw_data_html:str):
    soup = bs4.BeautifulSoup(raw_data_html, 'html.parser')

    full_offer_info = {}
    try:
            full_offer_info['offer_title'] = soup.find('h1', {'class':'offer-title big-text'}).get_text().strip()
    except AttributeError as ae:
            logger.error(f"Unable to open offer - it might have been removed. LINK: {link}")
            return None
    full_offer_info['price'] = soup.find('span', {'class':'offer-price__number'}).get_text().strip()

    details_group = soup.find('div', {'id':'parameters'})
    details_group = details_group.find_all('li', {'class':"offer-params__item"})
    full_offer_info["offer_details"] = {}
    for detail_container in details_group:
            detail_name = detail_container.find('span', {'class':'offer-params__label'}).get_text().strip()
            detail_value = detail_container.find('div',{'class':'offer-params__value'}).get_text().strip()
            full_offer_info["offer_details"][detail_name] = detail_value


    coords_1 = soup.find('div', {'class', 'gm-style'})
    coords_1 = coords_1.find_all('a', attrs={'href': re.compile("^https://")})
    coords_1 = [link.get('href') for link in coords_1][0]
    full_offer_info['coordinates'] = coords_1.split('ll=')[1].split('&')[0]

    try:    
            details_equipment = soup.find('div', {'id':'rmjs-1'})
            details_equipment = details_equipment.find_all('li', {'class':"parameter-feature-item"})
            full_offer_info["Wyposazenie"] = "|".join([item.get_text().strip() for item in details_equipment])
    except AttributeError as ae:

            logger.error(f"Unable to find equipment element - most probably it does not exist. LINK: {link}") 
    return full_offer_info