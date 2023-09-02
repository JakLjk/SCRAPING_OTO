from flask import Blueprint, jsonify, request
import json

from config import OperationTypes, ServConfig
from ..db_management_scripts.insert_link_into_db import add_link_to_db
from ..db_management_scripts.get_link_from_db import get_link_from_db, update_scrape_status, update_health_status
from ..db_management_scripts.insert_raw_data_into_db import add_raw_data_to_db
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


        
            



