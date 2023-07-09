from .num_pages import get_num_pages
from logger import logger
from config import Config


def scrape_links():
    logger.info("Beggining scraping of links.")
    logger.info("Fetching number of pages to parse.")
    num_pages = get_num_pages()
    logger.info(f"There are {num_pages} pages to parse.")
    logger.info(f"Generating link for every page with offer links")
    # List of links that have to be loaded in order to fetch information about all offers
    # Links are in reverse order, to fetch the last offers that are listed as first, which reduces
    # Problems with last page index moving forwards or backwards
    separate_page_links = (Config.OFFER_SCROLL_LIST_PAGE_LINK_PARSED.format(i)
                            for i in range(num_pages, 0, -1))
    logger.info(f"Generated {num_pages} links")

    for page_link in separate_page_links:
        # TODO implement retry method for each site being loaded
        # If retry will fail, go to next page
        page_raw_data = None
        print(page_link)