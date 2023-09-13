import requests
from config import ServConfig, OperationTypes


def post_link(link):
    request = requests.post(ServConfig.full_webhook_path, json={
        "Operation":OperationTypes.link_to_db,
        "inputLink":str(link)})
    data = request.json()
    status = data['Status']
    return status


