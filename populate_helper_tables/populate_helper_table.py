



from sqlalchemy.orm import Session
from sqlalchemy import exists, insert
from sqlalchemy.sql import text

from datetime import datetime
from time import sleep

from db import engine, offers_parsed, raw_offer_data_table
from config import Config
from logger import logger


wait_time_if_no_link_to_parse = Config.ETL.WAIT_IF_NO_OFFERS_TO_PARSE

def populate_helper_table():
    logger.info("Starting populate helper table function")
    while True:
        with Session(engine) as session:
            logger.info("Fetching condensed offer data from db...")
            raw_data_row = fetch_row_from_db(session)
            raw_data = raw_data_row.first()
            if raw_data is None:
                logger.info(f"There are no links to parse, checking again in {wait_time_if_no_link_to_parse} seconds")
                sleep(wait_time_if_no_link_to_parse)
                continue

            logger.info(f"Loading offer ID, offer details, equipment details...")
            foreign_offer_id = raw_data[0]
            offer_details = raw_data[1]
            offer_equipment = raw_data[2]

            logger.info("Structurizing condensed offer details into python dictionary.")
            separated_offer_details = {normalize_column_names(offer_col_name):offer_val 
                                    for offer_col_name, offer_val 
                                    in [val.split(":") for val  in offer_details.split("|")]}
            
            logger.info(f"Generating current datetime in sql format")
            curr_datetime = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

            logger.info(f"Populating offer dictionary with offer foreign key and current datetime")
            separated_offer_details["ID_O_P"] = int(foreign_offer_id)
            separated_offer_details["Generated_On_DateTime"] = curr_datetime
            logger.info("Fetching currently present columns in table")
            current_columns = get_currently_available_column_names(session, "separated_details_helper_table")
            logger.info("Running comparison, to see which columns have to be added...")
            columns_to_add = set(separated_offer_details.keys()) - set(current_columns)
            logger.info(f"Adding {len(columns_to_add)} columns that were not present before.")
            for column in columns_to_add:
                add_column(session, "separated_details_helper_table", column, "text")
            logger.info(f"Missing columns added.")
            logger.info(f"Inseting values into database")
            insert_value_in_db(session, 
                            "separated_details_helper_table", 
                            separated_offer_details)
            
            logger.info(f"Checking if additiona; equipment information is present.")
            if not offer_equipment == "NO_INFORMATION" and not offer_equipment == '':
                logger.info("Structurizing condensed equipment details into python dictionary.")
                separated_offer_equipment = {normalize_column_names(offer_col_name):1 
                                            for offer_col_name 
                                            in offer_equipment.split("|")}
                logger.info(f"Populating equipment dictionary with equipment foreign key and current datetime")
                separated_offer_equipment["ID_O_P"] = int(foreign_offer_id)
                separated_offer_equipment["Generated_On_DateTime"] = curr_datetime
                logger.info("Fetching currently present columns in table")
                current_columns = get_currently_available_column_names(session, "separated_equipment_helper_table")
                logger.info("Running comparison, to see which columns have to be added...")
                columns_to_add = set(separated_offer_equipment.keys()) - set(current_columns)
                logger.info(f"Adding {len(columns_to_add)} columns that were not present before.")
                for column in columns_to_add:
                    add_column(session, "separated_equipment_helper_table", column, "BOOLEAN")
                logger.info(f"Missing columns added.")
                logger.info(f"Inseting values into database")
                insert_value_in_db(session, 
                        "separated_equipment_helper_table", 
                        separated_offer_equipment)
        

def get_currently_available_column_names(session, table_name):
    sql_statement = \
    f"""SELECT column_name
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_NAME = '{str(table_name)}'"""
    return [name[0] for name in session.execute(text(sql_statement)).all()]
    
def add_column(session, table_name, column_name, data_type):
    sql_statement = \
    f"""ALTER TABLE {table_name}
    ADD {column_name} {data_type}"""
    session.execute(text(sql_statement))
    session.commit()

def fetch_row_from_db(session):
    sql_statement = \
    f"""SELECT ID_O_P, Offer_Details, Equipment_Details
    FROM offer_details_parsed
    WHERE NOT (EXISTS (SELECT * 
        FROM separated_details_helper_table
        WHERE offer_details_parsed.`ID_O_P` = separated_details_helper_table.`ID_O_P`))
    LIMIT 1 FOR UPDATE SKIP LOCKED""" 
    raw_data = session.execute(text(sql_statement))
    if raw_data is None:
        return None
    return raw_data

def insert_value_in_db(session, table_name, insert_dict):   
    col_names_list = list(insert_dict.keys())
    col_values_list = list(insert_dict.values())

    col_names_list = [f"`{name}`" for name in col_names_list]
    columns_parsed = ",".join(col_names_list)
    values_parsed = ",".join([f"\"{val}\"" for val in col_values_list])

    sql_statement = \
    f"""INSERT INTO {table_name} ({columns_parsed}) 
    VALUES ({values_parsed})"""
    print("XXX")
    print(sql_statement)
    session.execute(text(sql_statement))
    session.commit()

def normalize_column_names(col_name):
    REPLACE = {
    "ą":"a",
    "ź":"z",
    "ż":"z",
    "ł":"l",
    " ":"_",
    "ć":"c",
    "ń":"n",
    "ś":"s",
    "ó":"o",
    "ę":"e",
    "(":"",
    ")":"",
    "-":"_",
    ",":"_",
    "/":"_",
    ".":"_",
    ";":"_",
    ":":"_"
    }
    if type(col_name) == list:
        for old_val, new_val in REPLACE.items():
            col_name = [col_name.replace(old_val.lower(), new_val.lower()) for col_name in col_name]
        return col_name
    else:
        for old_val, new_val in REPLACE.items():
            col_name = col_name.replace(old_val.lower(), new_val.lower())
        return col_name
