import sys
sys.path.append('../')
from inspect_terminals import config

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

class MysqlDatabaseTwo:
    def __init__(self):
        self.__engine = create_async_engine(str(config.connection_mysql_two), echo=True)
        self.__session = sessionmaker(
            bind=self.__engine, class_=AsyncSession, expire_on_commit=False
        )

    @property
    def session(self):
        return self.__session()

    @property
    def engine(self):
        return self.__engine

