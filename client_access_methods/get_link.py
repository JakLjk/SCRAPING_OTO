import requests
from config import ServConfig, OperationTypes

def get_link():
    request  = requests.post(ServConfig.full_webhook_path, json= {
        "Operation":OperationTypes.link_from_db})
    data = request.json()
    status = data['Status']
    link = data['Link']
    return status, link