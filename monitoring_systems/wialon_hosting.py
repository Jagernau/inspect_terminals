from datetime import datetime, timedelta
from wialon.sdk import WialonSdk
import time
import sys
sys.path.append('../')
from inspect_terminals.my_logger import logger

class WialonHosting:
    def __init__(
            self, 
            wialon_token: str, 
            based_adres: str,
            ):
        self.wialon_token = wialon_token
        self.based_adres = based_adres
        self.sdk = WialonSdk(                
                is_development=True,
                scheme='https',
                host=str(based_adres),
                port=int(0),
                )

    def get_all_units(self):
        """
        Метод получения всех объектов Wialon hosting способом поиска
        """
        parameters_unit = {
        'spec':{
          'itemsType': "avl_unit",
          'propName': "sys_name",
          'propValueMask': "*",
          'sortType': "sys_name",
          'or_logic': 0
        },
        'force': 1,
        # 1024 последнее местопол +
        # 1 базовый +
        # 4 свойства билинга +
        # 128 админ записи +
        # 256 доп свойства +
        # 8 Произвольные поля +
        # 4096 датчики
        'flags': 5517, 
        'from': 0,
        'to': 0
        }
        self.sdk.login(str(self.wialon_token))
        units = self.sdk.core_search_items(parameters_unit)
        self.sdk.logout()
        return units["items"]

    def get_all_device_types(self):
        """
        Метод получения всех Типов терминалов
        """
        parameters_types = {
          'filterType': "name",
        }
        self.sdk.login(str(self.wialon_token))
        device_types = self.sdk.core_get_hw_types(parameters_types)
        self.sdk.logout()
        return device_types


    def get_all_users(self):
        """
        Метод получения всех юзеров Wialon hosting способом поиска
        """
        parameters_user = {
        'spec':{
          'itemsType': "user",
          'propName': "sys_name",
          'propValueMask': "*",
          'sortType': "sys_name",
          'or_logic': 0
        },
        'force': 1,
        # 1 базовый +
        # 4 билинг
        # 256 другие св-ва 
        'flags': 261, 
        'from': 0,
        'to': 0
        }
        self.sdk.login(str(self.wialon_token))
        units = self.sdk.core_search_items(parameters_user)
        self.sdk.logout()
        return units


    def create_terminal_comand(self, obj_id, comand_name, terminal_comand):
        """
        Метод создания комманды для отправки через Wialon
        """
        self.sdk.login(str(self.wialon_token))
        acc = self.sdk.unit_update_command_definition({
             "itemId": int(obj_id),
#             "id":<long>,
             "callMode": "create",
             "n": str(comand_name),
             "c": 'custom_msg',
             "l": '',
             "p": str(terminal_comand),
             # 34359738368 + создание редактирование команд
             # 17179869184 + просмотр команд
             # 16777216 + выполнение команд
             "a": int(51556384768)})
        time.sleep(2)
        self.sdk.logout()

    def exec_terminal_comand(self, obj_id, comand_name):
        """
        Метод отправки комманды команды через Wialon
        """
        time.sleep(2)
        self.sdk.login(str(self.wialon_token))
        comand = self.sdk.unit_exec_cmd({
            "itemId": int(obj_id),
            "commandName": str(comand_name),
            "linkType": '',
            "param": "",
            "timeout": int(10),
            "flags": int(0)
             })
        time.sleep(2)
        self.sdk.logout()


    def get_last_masseges_data(self, obj_id, curent_time):
        """
        Метод получение сообщений от терминала Wialon
        """
        time.sleep(2)
        self.sdk.login(str(self.wialon_token))
        comand_result = self.sdk.messages_load_last({
            "itemId": int(obj_id),
            "lastTime": curent_time,
            "lastCount": 100,
            "flags": 512,
            "flagsMask": int(0),
            "loadCount": 100
             })
        self.sdk.logout()
        return comand_result
