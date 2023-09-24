import requests
from config import ServConfig, OperationTypes

def get_raw_data():
    request = requests.post(ServConfig.full_webhook_path, json= {
        "Operation":OperationTypes.get_raw_data})
    data = request.json()
    if data["Status"] == OperationTypes.status_failed:
        raise ValueError(data["statusComment"])
    return data

def update_etl_status(raw_data_id, link, new_status):
    request = requests.post(ServConfig.full_webhook_path, json = {
        "Operation":OperationTypes.update_etl_status,
        "id":raw_data_id,
        "Link":link,
        "New_Status": new_status})
    data = request.json()
    return data

def push_offer_details_to_db(link:str,
                           offer_title:str,
                           offer_price:str,
                           offer_details:str,
                           offer_equipment_details:str,
                           offer_coordinates:str):
    request = requests.post(ServConfig.full_webhook_path, json = {
        "Operation":OperationTypes.push_offer_details_to_db,
        "link":link,
        "offer_title":offer_title,
        "offer_price":offer_price,
        "offer_details":offer_details,
        "offer_equipment_details":offer_equipment_details,
        "offer_coordinates":offer_coordinates})
    data = request.json()
    if data["Status"] == OperationTypes.status_failed:
        raise ValueError(data["statusComment"])
    return data
