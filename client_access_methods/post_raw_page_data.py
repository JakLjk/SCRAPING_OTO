import requests
from config import ServConfig, OperationTypes


def post_raw_data(raw_data,webpage_stype, used_link):
    request = requests.post(ServConfig.full_webhook_path, json={
        "Operation":OperationTypes.raw_data_to_db,
        "rawData":raw_data,
        "webpageStyle":webpage_stype,
        "usedLink":used_link})
    data = request.json()
    status = data['Status']
    return status
    