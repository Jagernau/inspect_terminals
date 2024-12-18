from os import environ as envi
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine

load_dotenv()


DB_HOST_TWO = envi.get('DB_HOST_TWO')
MYSQL_USER_TWO = envi.get('MYSQL_USER_TWO')
MYSQL_DB_NAME_TWO = envi.get('MYSQL_DB_NAME_TWO')
MYSQL_PASSWORD_TWO = envi.get('MYSQL_PASSWORD_TWO')
MYSQL_PORT_TWO = envi.get('MYSQL_PORT_TWO')
connection_mysql_two = f"mysql+aiomysql://{MYSQL_USER_TWO}:{MYSQL_PASSWORD_TWO}@{DB_HOST_TWO}:{MYSQL_PORT_TWO}/{MYSQL_DB_NAME_TWO}"
DB_ENGINE = create_async_engine(connection_mysql_two, echo=True)

GLONASS_BASED_ADRESS=envi.get('GLONASS_BASED_ADRESS')
GLONASS_LOGIN=envi.get('GLONASS_LOGIN')
GLONASS_PASS=envi.get('GLONASS_PASS')
GLONASS_PARENT_ID=envi.get('GLONASS_PARENT_ID')

