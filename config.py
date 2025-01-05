from os import environ as envi
from dotenv import load_dotenv

load_dotenv()


DB_HOST_TWO = envi.get('DB_HOST_TWO')
MYSQL_USER_TWO = envi.get('MYSQL_USER_TWO')
MYSQL_DB_NAME_TWO = envi.get('MYSQL_DB_NAME_TWO')
MYSQL_PASSWORD_TWO = envi.get('MYSQL_PASSWORD_TWO')
MYSQL_PORT_TWO = envi.get('MYSQL_PORT_TWO')
connection_mysql = f"mysql+mysqlconnector://{MYSQL_USER_TWO}:{MYSQL_PASSWORD_TWO}@{DB_HOST_TWO}:{MYSQL_PORT_TWO}/{MYSQL_DB_NAME_TWO}"

MONITORING_CONFIG = {
    "glonass": {
        "login": envi.get('GLONASS_LOGIN'),
        "password": envi.get('GLONASS_PASS'),
        "address": envi.get('GLONASS_BASED_ADRESS'),
        "user_id": envi.get('GLONASS_USR_ID'),
        "parent_id": envi.get('GLONASS_PARENT_ID'),
    },
}

