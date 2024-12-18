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

