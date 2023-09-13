import requests
from server_side_management.webhook.db_model import links
from server_side_management.webhook import db
from config import ServConfig, OperationTypes

def get_link():
    request  = requests.post(ServConfig.full_webhook_path, json= {
        "Operation":OperationTypes.link_from_db})
    data = request.json()
    status = data['Status']
    link = data['Link']
    return {"Status":status, "Link":link}

def change_link_status(link, new_status):
    request = requests.post(ServConfig.full_webhook_path, json={
        "Operation":OperationTypes.update_link_status,
        "Link":str(link),
        "linkStatus":new_status})
    data = request.json()
    status = data['Status']
    link = data['Link']
    return status, link
    
def update_error_message(link, message):
    request = requests.post(ServConfig.full_webhook_path, json={
        "Operation":OperationTypes.update_error_message,
        "Link":str(link),
        "errorMessage":message})
    data = request.json()
    return data

def change_link_health_status(link, new_status):
    request = requests.post(ServConfig.full_webhook_path, json={
        "Operation":OperationTypes.update_link_health_status,
        "Link":str(link),
        "linkHealthStatus":new_status})
    data = request.json()
    status = data['Status']
    link = data['Link']
    return status, link