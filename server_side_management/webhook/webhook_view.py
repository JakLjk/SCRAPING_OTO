from flask import Blueprint, jsonify, request
import json

from config import OperationTypes, ServConfig
from ..db_management_scripts.insert_link_into_db import add_link_to_db
from ..db_management_scripts.get_link_from_db import get_link_from_db, update_scrape_status, update_health_status
from ..db_management_scripts.insert_raw_data_into_db import add_raw_data_to_db
from ..db_management_scripts.raw_page_interpreter_methods import get_raw_from_db, push_offer_details_parsed_to_db, update_etl_status_performed
from ..db_management_scripts.populate_helper_table_methods import fetch_row_from_db, get_currently_available_column_names, add_column, insert_data_into_helper_table
from logger import logger

webhook = Blueprint('webhook', __name__)

@webhook.route(ServConfig.webhook_subdirectory, methods=['POST'])
def data_hook():
    if request.method == 'POST':
        data = json.loads(request.data)

        # Load scraped link into db
        if OperationTypes.link_to_db == data["Operation"]:
            input_link = data["inputLink"]
            logger.info(f"Inserting link to db: {input_link}")
            try: 
                add_link_to_db(input_link)
                logger.info("Link was inserted into db.")
            except ValueError as ve:
                logger.error(str(ve))
                return jsonify({"Status":OperationTypes.status_failed})
            return jsonify({"Status":OperationTypes.status_success})
        
        # Load link from db
        elif OperationTypes.link_from_db == data["Operation"]:
            try:
                link = get_link_from_db()   
                return jsonify({"Status": OperationTypes.status_success,
                                "Link":link})
            except ValueError as ve:
                logger.error(str(ve))
                return jsonify({"Status":OperationTypes.status_failed,
                                "Link":None})
            
        elif OperationTypes.update_link_status == data["Operation"]:
            link = data["Link"]
            link_status = data["linkStatus"]
            update_scrape_status(link, link_status)
            return jsonify({"Status": OperationTypes.status_success,
                                "Link":link})
    
        elif OperationTypes.update_link_health_status == data["Operation"]:
            link = data["Link"]
            link_health_status = data["linkHealthStatus"] 
            update_health_status(link, link_health_status)
            return jsonify({"Status": OperationTypes.status_success,
                                "Link":link})
        
        elif OperationTypes.raw_data_to_db == data["Operation"]:
            raw_data = data["rawData"]
            used_link = data["usedLink"] 
            add_raw_data_to_db(raw_data, used_link)
            return jsonify({"Status": OperationTypes.status_success})
        
        elif OperationTypes.get_raw_data == data["Operation"]:
            try:
                raw_data = get_raw_from_db()
            except ValueError as ve:
                logger.warning(ve)
                return ({"Status":OperationTypes.status_failed,
                  "statusComment":ve})
            link = raw_data.Used_Link
            raw_data = raw_data.Raw_Data
            return jsonify({"Status": OperationTypes.status_success,
                                "Link":link,
                                "rawData":raw_data})

        elif OperationTypes.push_offer_details_to_db == data["Operation"]:
            link = data["link"]
            offer_title = data["offer_title"] 
            offer_price = data["offer_price"]
            offer_details = data["offer_details"]
            offer_equipment_details = data["offer_equipment_details"]
            offer_coordinates = data["offer_coordinates"]
            try:
                push_offer_details_parsed_to_db(link,
                                                offer_title,
                                                offer_price,
                                                offer_details,
                                                offer_equipment_details,
                                                offer_coordinates)
                return jsonify({"Status": OperationTypes.status_success})
            except ValueError as ve:
                logger.info(ve)
                ({"Status":OperationTypes.status_failed,
                  "statusComment":ve})
        
        elif OperationTypes.update_etl_status == data["Operation"]:
            link = data["Link"]
            new_status = data["New_Status"]
            update_etl_status_performed(link, new_status)
            return jsonify({"Status": OperationTypes.status_success})
        
        elif OperationTypes.get_row_data_for_helper_table == data["Operation"]:
            try:
                result = fetch_row_from_db()
                id = result[0]
                off_details = result[1]
                eq_details = result[2]
                return jsonify({"Status": OperationTypes.status_success,
                                "ID_O_P":id,
                                "offerDetails":off_details,
                                "equipmentDetails":eq_details})
            except ValueError as ve:
                logger.warn(ve)
                return jsonify({"Status": OperationTypes.status_failed})

        elif OperationTypes.get_currently_available_column_names == data["Operation"]:
            table_name = data["tableName"]
            result = get_currently_available_column_names(table_name)
            return jsonify({"Status": OperationTypes.status_success,
                            "columnNames":result})

        elif OperationTypes.add_column_to_table == data["Operation"]:
            table_name = data["tableName"]
            column_name = data["columnName"]
            data_type = data["dataType"]
            add_column(table_name, column_name, data_type)
            return jsonify({"Status": OperationTypes.status_success})

        elif OperationTypes.insert_data_into_helper_table == data["Operation"]:
            table_name = data["tableName"]
            insert_dict = data["insertDict"]
            insert_data_into_helper_table(table_name, insert_dict)
            return jsonify({"Status": OperationTypes.status_success})





            



