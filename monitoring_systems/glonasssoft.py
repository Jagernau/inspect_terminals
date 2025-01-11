import asyncio
import aiohttp
from random import uniform
from datetime import datetime, timedelta
import sys
sys.path.append('../')
from inspect_terminals.my_logger import logger

class Glonasssoft:
    def __init__(
            self, 
            login: str, 
            password: str, 
            based_adres: str,
            glonass_user_id: str,
            glonass_parent_id: str
            ):
        self.login = login
        self.password = password
        self.based_adres = based_adres
        self.glonass_user_id = glonass_user_id
        self.glonass_parent_id = glonass_parent_id

    async def gen_random_delay(self):
        await asyncio.sleep(uniform(1.1, 1.7))

    async def token(self):
        """Получение Токена Глонассофт"""
        await self.gen_random_delay()
        url = f"{self.based_adres}v3/auth/login"
        data = {"login": self.login, "password": self.password}
        headers = {"Content-type": "application/json", "accept": "json"}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data, headers=headers) as response:
                if response.status == 200:
                    return (await response.json()).get("AuthId")
                else:
                    logger.warning("Не получен ТОКЕН")
                    return None

    async def _get_request(self, url, token):
        """Асинхронный универсальный метод для GET-запросов"""
        headers = {
            "X-Auth": f"{token}",
            "Content-type": "application/json",
            "Accept": "application/json",
        }
        await self.gen_random_delay()
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.warning(f"Ошибка GET-запроса на {url}")
                    return None

    async def _post_request(self, url, token, data: dict):
        """Асинхронный универсальный метод для POST-запросов"""
        headers = {
            "X-Auth": f"{token}",
            "Content-type": "application/json",
            "Accept": "application/json",
        }
        await self.gen_random_delay()
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.warning(f"Ошибка POST-запроса на {url}")
                    return None

    async def get_all_vehicles_new(self, token):
        """Асинхронный метод получения всех объектов"""
        data = {"parentId": str(self.glonass_parent_id)}
        await asyncio.sleep(1)
        return await self._post_request(f"{self.based_adres}v3/vehicles/find", token, data)


    async def put_terminal_comands(self, gl_token: str, destinationid: str, taskdata: str):
        """
        Асинхронная отправка команды в терминал.
        """
        url = f"{self.based_adres}commands/put"
        headers = {
            "X-Auth": gl_token,
            "Content-Type": "application/json",
        }
        data = [{
            "sourceid": self.glonass_user_id,
            "destinationid": destinationid,
            "tasktype": 0,
            "taskdata": taskdata,
            "trycount": 0,
            "TryMax": "3",
            "answer": "",
            "owner": self.glonass_parent_id,
        }]

        await self.gen_random_delay()
        async with aiohttp.ClientSession() as session:
            async with session.put(url, headers=headers, json=data) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.warning(f"Ошибка отправки команды на {url}: {response.status} {await response.text()}")
                    return None


    async def get_terminal_answer(self, gl_token: str, imei: str):
        """
        Асинхронное получение ответов от терминала.
        """
        url = f"{self.based_adres}commands"

        past_time = datetime.now() - timedelta(minutes=10)
        past_time = past_time.strftime('%Y-%m-%dT%H:%M:%S.%f')

        future_time = datetime.now() + timedelta(minutes=10)
        future_time = future_time.strftime('%Y-%m-%dT%H:%M:%S.%f')

        data = str({
            "imei": imei,
            "start": past_time,
            "end": future_time,
        })
        params = {
            "q": data,
            "sort": '[{"property":"createtime","direction":"DESC"}]',
        }
        headers = {
            "X-Auth": gl_token,
        }

        await self.gen_random_delay()
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.warning(f"Ошибка получения команд с {url}: {response.status} {await response.text()}")
                    return None


