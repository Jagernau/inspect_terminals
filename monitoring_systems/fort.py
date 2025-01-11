import asyncio
import aiohttp
from random import uniform
from datetime import datetime, timedelta
import sys
sys.path.append('../')
from inspect_terminals.my_logger import logger

class Fort:
    def __init__(
            self, 
            login: str, 
            password: str, 
            based_adres: str,
            ):
        self.login = login
        self.password = password
        self.based_adres = based_adres

    async def gen_random_delay(self):
        await asyncio.sleep(uniform(1.1, 1.7))

    async def _get_request(self, url, token, params):
        """Универсальный метод для выполнения GET-запросов"""
        headers = {
                    'Content-type': 'application/json', 
                    'Accept': 'application/json', 
                    'SessionId': token
                }
        await self.gen_random_delay()
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.warning(f"Ошибка GET-запроса на {url}")
                    return None

    async def token(self):
        """Получение Токена Fort"""
        await self.gen_random_delay()
        url = f'{self.based_adres}v1/connect'
        params = {
                'login': self.login,
                'password': self.password,
                'lang': 'ru-ru',
                'timezone': '+3'
        }
        headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=headers) as response:
                    if response.status == 200:
                        session_id = response.headers.get('SessionId')
                        if session_id:
                            return session_id
                        else:
                            logger.warning("SessionId отсутствует в заголовках ответа")
                            return None
                    else:
                        logger.warning(f"Ошибка при получении токена: {response.status}")
                        return None
        except aiohttp.ClientError as e:
            logger.error(f"Ошибка сети при получении токена: {e}")
            return None


    async def get_all_vehicles(self,token):
        params = {
                'SessionId': str(token),
                'companyId': 0
        }
        return await self._get_request(f"{self.based_adres}v1/getobjectslist", token, params=params) 

