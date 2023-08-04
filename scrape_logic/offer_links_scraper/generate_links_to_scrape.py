
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from datetime import date

import bs4

from logger import logger
from config import Config

from response_methods import pick_selenium_driver

from .generate_manufacturer_links import get_year_manufacturer_separated_links
from .get_num_pages import get_num_pages


def generate_links_to_scrape():
    link_part_with_page_id = Config.LinksSetup.TEMPLATE_LINK_PAGE_NUM

    split_links = get_year_manufacturer_separated_links()
    all_links = []
    for link in split_links:
        num_pages = get_num_pages(link)
        if num_pages == None or num_pages == 1:
            link = link + link_part_with_page_id.format(1)
            all_links.append(link)
        else:
            link_with_page_id = link + link_part_with_page_id
            separate_page_links = [link_with_page_id.format(i)
                        for i in range(num_pages, 0, -1)]
            all_links.append(separate_page_links)
    return all_links