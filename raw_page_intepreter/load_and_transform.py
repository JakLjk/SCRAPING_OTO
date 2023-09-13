# TODO Load offer data from databas
# TODO Convert data into usefull format 
# TODO load into proper db table
from sqlalchemy.orm import Session
from sqlalchemy import exists, insert


from datetime import datetime

import bs4
import re

from config import Config
from db import engine, raw_offer_data_table, offers_parsed
from logger import logger

from server_side_management.webhook import db


parse_previously_parsed = Config.ETL.PROCESS_LINKS_PREVIOUSLY_PARSED

def load_raw_offer_data():
    with Session(engine) as session:
        if parse_previously_parsed:
                raw_data_row = (session.query(raw_offer_data_table)
                .with_for_update(skip_locked=True)
                .first())
        else:
                raw_data_row = (session.query(raw_offer_data_table)
                .filter(~ exists().where(offers_parsed.c.Link==raw_offer_data_table.c.Used_Link))
                .with_for_update(skip_locked=True)
                .first())
               
        if raw_data_row is None:
               return None
        return {"link":raw_data_row.Used_Link, "raw_data":raw_data_row.Raw_Data}
        

def write_offer_data_to_db(link:str,
                           offer_title:str,
                           offer_price:str,
                           offer_details:str,
                           offer_equipment_details:str,
                           offer_coordinates:str):
        
        with Session(engine) as session:
                curr_date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
                statement = (insert(offers_parsed)
                        .values(Parsing_DateTime=curr_date,
                                Link=link,
                                Offer_Title=offer_title,
                                Offer_Price=offer_price,
                                Offer_Details=offer_details,
                                Equipment_Details=offer_equipment_details,
                                Coordinates=offer_coordinates))
                session.execute(statement)
                session.commit()

def set_link_scrape_status_to_true(link:str):
        with Session(engine) as session:
                num_rows_updated = (session.query(raw_offer_data_table)
                                .filter_by(Used_Link=link)
                                .update(dict(ETL_Performed_Status=True)))
                session.commit()
                


def scrape_data_from_raw(link:str, raw_data_html:str, webpage_style:str):
    soup = bs4.BeautifulSoup(raw_data_html, 'html.parser')
    if webpage_style == "NEW":
        return scrape_new_layout(soup, link)
    elif webpage_style == "OLD":
        return scrape_legacy_layout(soup, link)


def scrape_legacy_layout(soup:bs4.BeautifulSoup, link):
    logger.info("Using old offer scrapper")
    full_offer_info = {}
    try:
            full_offer_info['offer_title'] = soup.find('h1', {'class':'offer-title big-text'}).get_text().strip()
    except AttributeError as ae:
            logger.error(f"OLD: Unable to fetch offer title. LINK: {link}")
            return AttributeError("No Title Information")
    full_offer_info['price'] = soup.find('span', {'class':'offer-price__number'}).get_text().strip()
    

    details_group = soup.find('div', {'id':'parameters'})
    details_group = details_group.find_all('li', {'class':"offer-params__item"})
    separate_details = []
    for detail_container in details_group:
        detail_name = detail_container.find('span', {'class':'offer-params__label'}).get_text().strip()
        detail_value = detail_container.find('div',{'class':'offer-params__value'}).get_text().strip()
        separate_details.append(f"{detail_name}:{detail_value}")
        
    full_offer_info["offer_details"] = "|".join(separate_details)
    coords_1 = soup.find('div', {'class', 'gm-style'})
    coords_1 = coords_1.find_all('a', attrs={'href': re.compile("^https://")})
    coords_1 = [link.get('href') for link in coords_1][0]
    full_offer_info['coordinates'] = coords_1.split('ll=')[1].split('&')[0]

    try:    
            details_equipment = soup.find('div', {'class':'offer-features__row'})
            details_equipment = details_equipment.find_all('li', {'class':"parameter-feature-item"})
            full_offer_info["equipment"] = "|".join([item.get_text().strip() for item in details_equipment])
    except AttributeError as ae:
            full_offer_info["equipment"] = "NO_INFORMATION"
            logger.error(f"Unable to find equipment element - most probably it does not exist. LINK: {link}") 

    return full_offer_info

def scrape_new_layout(soup:bs4.BeautifulSoup, link):
    logger.info("Using new layout scraper")
    full_offer_info = {}
    try:
            title_reg = re.compile('offer-title.big-text.*')
            full_offer_info['offer_title'] = soup.find('h3', {'class':title_reg}).get_text().strip()
    except AttributeError as ae:
            logger.error(f"Unable to fetch offer title. LINK: {link}")
            return AttributeError("No Title Information")
    price_reg = re.compile("offer-price__number.*")
    full_offer_info['price'] = soup.find('h3', {'class':price_reg}).get_text().strip()
    
    details_reg = re.compile('.*e1iqsx44')
    details_group = soup.find('div', {'class':details_reg})
    detail_reg_2 = re.compile('.*e1iqsx43')
    details_group = details_group.find_all('div', {'class':detail_reg_2})
    separate_details = []
    for detail_container in details_group:
        name_reg = re.compile('.*ooa-1h25pzj')
        detail_name = detail_container.find('p', {'class':name_reg}).get_text().strip()
        try:
            value_reg = re.compile('.*ooa-189feh2')
            detail_value = detail_container.find('a',{'class':value_reg}).get_text().strip()
        except AttributeError as ae:
            try:
                value_reg = re.compile('e1cl5iuz1 ooa-ywgrlx er34gjf0')
                detail_value = detail_container.find('p',{'class':value_reg}).get_text().strip()
            except AttributeError as ae:
                raise ae  
                
        separate_details.append(f"{detail_name}:{detail_value}")
        
    full_offer_info["offer_details"] = "|".join(separate_details)

    coords_1 = soup.find('div', {'class', 'gm-style'})
    coords_1 = coords_1.find_all('a', attrs={'href': re.compile("^https://")})
    coords_1 = [link.get('href') for link in coords_1][0]
    full_offer_info['coordinates'] = coords_1.split('ll=')[1].split('&')[0]

    try:
        details_equipment = soup.find_all('p', {'class','evccnj10 ooa-1i4y99d er34gjf0'})
        full_offer_info["equipment"] = "|".join([item.get_text().strip() for item in details_equipment])
        if full_offer_info == '':
             full_offer_info["equipment"] = "EMPTY_CONTAINER" 
    except AttributeError as ae:
            full_offer_info["equipment"] = "NO_INFORMATION"
            logger.error(f"Unable to find equipment element - most probably it does not exist. LINK: {link}") 
    return full_offer_info