import json
import requests
import time

import sys
sys.path.append('../')
from information_services_backend import config
from information_services_backend.my_logger import logger
import random

class Glonasssoft:
    """ 
    Получение данных с систем мониторинга Глонассофт
    """
    def __init__(self, login: str, password: str, based_adres: str):
        self.login = login
        self.password = password
        self.based_adres = based_adres

    def gen_random_num(self):
        return random.uniform(1.1, 1.7)

    def token(self):
        """Получение Токена Глонассофт"""
        time.sleep(self.gen_random_num())
        url = f'{self.based_adres}v3/auth/login'
        data = {'login': self.login, 'password': self.password}
        headers = {'Content-type': 'application/json', 'accept': 'json'}
        response = requests.post(url, data=json.dumps(data), headers=headers)
        if response.status_code == 200:
            return response.json()["AuthId"]
        else:
            time.sleep(self.gen_random_num())
            response = requests.post(url, data=json.dumps(data), headers=headers)
            if response.status_code == 200:
                return response.json()["AuthId"]
            else:
                logger.info(f"Не получен ТОКЕН")
                return None


    def _get_request(self, url, token):
        """Универсальный метод для выполнения GET-запросов"""
        headers = {
            "X-Auth": f"{token}",
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }
        time.sleep(self.gen_random_num())
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            time.sleep(self.gen_random_num())
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                logger.info(f"Не получен GET")
                return None

    def _post_request(self, url, token, data: dict):
        """Универсальный метод для выполнения POST """
        headers = {
            "X-Auth": f"{token}",
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }
        time.sleep(self.gen_random_num())
        response = requests.post(url, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            return response.json()
        else:
            time.sleep(self.gen_random_num())
            response = requests.post(url, headers=headers, data=json.dumps(data))
            if response.status_code == 200:
                return response.json()
            else:
                logger.info(f"Не получен POST")
                return None

    def get_all_vehicles_new(self, token: str, parentId: str):
        """
        Метод получения всех объектов glonasssoft
        """
        data = {
                "parentId": str(parentId)
            }
        time.sleep(1)
        return self._post_request(f"{self.based_adres}v3/vehicles/find", token, data)
    

