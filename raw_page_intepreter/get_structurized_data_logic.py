from .load_and_transform import load_raw_offer_data, scrape_data_from_raw


def get_structurized_data():
    while True:
        row_data = load_raw_offer_data()
        link = row_data["link"]
        raw_data = row_data["raw_data"]


        scraped_data = scrape_data_from_raw()
        print('TEST------------------------------\n\n\n\n\n\n\n XXXXXXXXXXXXXX')
        print(scraped_data)

        break