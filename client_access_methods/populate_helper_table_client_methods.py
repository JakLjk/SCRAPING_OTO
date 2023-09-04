import requests
from config import ServConfig, OperationTypes

def get_raw_data_for_helper_tables():
    request = requests.post(ServConfig.full_webhook_path, json= {
        "Operation":OperationTypes.get_row_data_for_helper_table})
    data = request.json()
    return data


def get_currently_available_column_names(table_name):
    request = requests.post(ServConfig.full_webhook_path, json = {
        "Operation":OperationTypes.get_currently_available_column_names,
        "tableName":table_name})
    data = request.json()
    return data["columnNames"]


def add_column(table_name, column_name, data_type):
    request = requests.post(ServConfig.full_webhook_path, json = {
        "Operation":OperationTypes.add_column_to_table,
        "tableName":table_name,
        "columnName":column_name,
        "dataType":data_type})
    data = request.json()
    return data

def insert_value_in_db(table_name, insert_dict):
    request = requests.post(ServConfig.full_webhook_path, json = {
        "Operation":OperationTypes.insert_data_into_helper_table,
        "tableName":table_name,
        "insertDict":insert_dict})
    data = request.json()
    return data