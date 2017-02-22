import mysql.connector
from config import AppConfig

config = AppConfig()


def get_mysql_cnx():
    """Returns a MySQL connection"""
    return mysql.connector.connect(
        user=config.db.user, password=config.db.password, host=config.db.host, database=config.db.database)