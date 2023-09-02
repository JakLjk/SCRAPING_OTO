from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from config import ServConfig


__db_username = ServConfig.DB_USERNAME
__db_password = ServConfig.DB_PASSWORD
__host = ServConfig.DB_HOST
__database = ServConfig.DATABASE_NAME
DB_URI = f"mariadb+mariadbconnector://{__db_username}:{__db_password}@{__host}/{__database}"

db = SQLAlchemy()

def init_server():
    serv = Flask(__name__)
    serv.config["SECRET_KEY"] = ServConfig.secret_Key
    serv.config["SQLALCHEMY_DATABASE_URI"] = DB_URI
    db.init_app(serv)

    from .webhook_view import webhook

    serv.register_blueprint(webhook, url_prefix='/')

    return serv

