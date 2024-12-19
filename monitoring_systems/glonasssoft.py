import asyncio
import json
import aiohttp
from random import uniform
from collections import Counter
from inspect_terminals.my_logger import logger

class Glonasssoft:
    def __init__(self, login: str, password: str, based_adres: str):
        self.login = login
        self.password = password
        self.based_adres = based_adres

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

    async def get_all_vehicles_new(self, token: str, parentId: str):
        """Асинхронный метод получения всех объектов"""
        data = {"parentId": str(parentId)}
        await asyncio.sleep(1)
        return await self._post_request(f"{self.based_adres}v3/vehicles/find", token, data)


    async def put_terminal_comands(self, token: str, sourceid: str, destinationid: str, taskdata: str, owner: str):
        """
        Асинхронная отправка команды в терминал.

        Аргументы:
            token: Токен авторизации.
            sourceid: Идентификатор источника.
            destinationid: Идентификатор получателя.
            taskdata: Команда для терминала.
            owner: Владелец команды.
        Возвращает:
            Ответ сервера в формате JSON или сообщение об ошибке.
        """
        url = f"{self.based_adres}api/commands/put"
        headers = {
            "X-Auth": token,
            "Content-Type": "application/json",
        }
        data = [{
            "sourceid": sourceid,
            "destinationid": destinationid,
            "tasktype": 0,
            "taskdata": taskdata,
            "trycount": 0,
            "TryMax": "3",
            "answer": "",
            "owner": owner,
        }]

        await self.gen_random_delay()
        async with aiohttp.ClientSession() as session:
            async with session.put(url, headers=headers, json=data) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.warning(f"Ошибка отправки команды на {url}: {response.status} {await response.text()}")
                    return None


    async def get_terminal_answer(self, token: str, imei: str, start: str, end: str):
        """
        Асинхронное получение ответов от терминала.

        Аргументы:
            token: Токен авторизации.
            imei: IMEI терминала.
            start: Дата начала (в формате YYYY-MM-DD).
            end: Дата окончания (в формате YYYY-MM-DD).
        Возвращает:
            Ответ сервера в формате JSON или сообщение об ошибке.
        """
        url = f"{self.based_adres}api/commands"
        data = str({
            "imei": imei,
            "start": start,
            "end": end,
        })
        params = {
            "q": data,
            "sort": '[{"property":"createtime","direction":"DESC"}]',
        }
        headers = {
            "X-Auth": token,
        }

        await self.gen_random_delay()
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.warning(f"Ошибка получения команд с {url}: {response.status} {await response.text()}")
                    return None


