
import os, sys

from scrape_logic import scrape_links, scrape_offer
from raw_page_intepreter import get_structurized_data
from populate_helper_tables import populate_helper_table
from server_side_management import start_server

from logger import logger

# Adding necessary paths into PATH for the time of session run
sys.path.append(os.path.join(os.path.dirname(__file__), "response_methods"))

user_args = [arg.lower() for arg in sys.argv[1:]]
expectad_args = {"-o":"Initializes scraping offers based on links available in Database.",
                 "-l":"Initializes scraping links based on primary link passed in config.",
                 "-etl":"Initializes process of parsing raw html contained in DB into structurized data",
                 "-detl":"Initializes process of getting additional details from mined webpage data - uses data from etl process",
                 "-h":"Displays help."}

def main():



    if len(user_args) == 0:
        logger.info(f"No arguments were passed, [-h for help].")

    if "-h" in user_args:
        arg_string ="\n" +"\n".join([f"{key}: {val}" for key, val in expectad_args.items()])
        print(f"""Arguments that can be utilized in this script: {arg_string}""")


    # TODO Accept l or o
    # TODO l [optional argument with voivodeships to parse]
    if "-s" in user_args:
        start_server()

    if "-l" in user_args:
        scrape_links()

    if "-o" in user_args:
        scrape_offer()

    if "-etl" in user_args:
        get_structurized_data()
    
    if "-detl" in user_args:
        populate_helper_table()

    logger.info("+++Program has finished running+++")

if __name__=="__main__":
    main()