from time import sleep
from monitoring_systems import wialon_hosting as wh
from collections import Counter
from my_logger import logger as log
from comands_dict import commands as comm_dict
from my_logger import logger as log
import asyncio
import re
import time
from wialon.sdk import WialonError, SdkException

class WialonLocalAction:
    def __init__(self, 
                 wialon_hosting_token,
                 wialon_hosting_adres,
                 ) -> None:
        self.wialon_hosting_class = wh.WialonHosting(
                wialon_token=wialon_hosting_token,
                based_adres=wialon_hosting_adres
                )

    async def get_wialon_hosting_odjects(self):
        "Возвращает все объекты, сортированные по количесту типы терминылов"
        try:
            all_vehicles = None
            sorted_device_type_counts = None
            all_vehicles = self.wialon_hosting_class.get_all_units()
            all_devices = self.wialon_hosting_class.get_all_device_types()
            clear_all_vehicles = []
            for vehicle in all_vehicles:
                if vehicle["act"] == 1:
                    curent_types = [str(re.sub(r'\d', '', str(device["name"].split(' ')[0]))).upper() for device in all_devices if device["id"] == vehicle['hw']]
                    vehicle['deviceTypeName'] = curent_types[0] if len(curent_types) >= 1 else None
                    clear_all_vehicles.append({
                                'deviceTypeName': curent_types[0] if len(curent_types) >=     1 else None,
                                "imei": vehicle["uid"],
                                "id": vehicle["id"],
                                "name": vehicle["nm"],
                            })
                if clear_all_vehicles:
                    device_types = [item['deviceTypeName'] for item in clear_all_vehicles if 'deviceTypeName' in item]
                    device_type_counts = Counter(device_types)
                    sorted_device_type_counts = dict(
                        sorted(device_type_counts.items(), key=lambda x: x[1], reverse=True))

        except (Exception, WialonError, SdkException) as e:
            log.error(f"Ошибка в получении данных {e}")
        else:
            if clear_all_vehicles and sorted_device_type_counts:
                print(sorted_device_type_counts)
                return clear_all_vehicles, sorted_device_type_counts
            else:
                return None


    def put_comands(self, 
                          all_vehicles,
                          sorted_device_type_counts,
                          ):
        "Рассылает команды на терминалы"
        for device_type, _ in sorted_device_type_counts.items():
            for vehicle in all_vehicles:
                if 'deviceTypeName' in vehicle and  vehicle['deviceTypeName'] == device_type:
                    terminal_id = int(vehicle["id"])
                    clear_device_type = device_type

                    if clear_device_type in comm_dict:
                        command = comm_dict[clear_device_type]["iccid"]["command"]
                        self.wialon_hosting_class.create_terminal_comand(
                            obj_id=terminal_id, 
                            comand_name="GET_Iccid", 
                            terminal_comand=command
                            )
                        sleep(5)
                        self.wialon_hosting_class.exec_terminal_comand(
                            obj_id=terminal_id, 
                            comand_name="GET_Iccid"
                            )


    def answer_objects(self,
                             all_vehicles, 
                             sorted_device_type_counts,
                             ):
        "Собирает ответы с терминалов"
        answers = []
        try:
            for device_type, _ in sorted_device_type_counts.items():
                for vehicle in all_vehicles:
                    if 'deviceTypeName' in vehicle and vehicle['deviceTypeName'] == device_type:
                        terminal_id = vehicle["id"]
                        # Время для запроса
                        request_time = int(time.time()) - 600

                        answer = self.wialon_hosting_class.get_last_masseges_data(
                                obj_id=terminal_id,
                                curent_time=request_time
                                )
                        if answer and len(answer) >= 1:
                            try:
                                pattern = r"\b8\d{17,19}\b"

                                def find_iccid(obj):
                                    """Рекурсивный поиск ICCID в JSON."""
                                    matches = []
                                    if isinstance(obj, dict):
                                        for key, value in obj.items():
                                            # Проверяем ключ
                                            matches.extend(re.findall(pattern, str(key)))
                                            # Проверяем значение
                                            matches.extend(find_iccid(value))
                                    elif isinstance(obj, list):
                                        for item in obj:
                                            # Проверяем каждый элемент списка
                                            matches.extend(find_iccid(item))
                                    elif isinstance(obj, (str, int, float)):  # Если значение - строка или число
                                        matches.extend(re.findall(pattern, str(obj)))
                                    return matches

                                digits = find_iccid(answer)
                                result = digits[0] if digits else ''

                            except (Exception, WialonError, SdkException) as e:
                                log.error(f"ошибка в приёме и обработке ответа {answer}  {e}")
                                continue
                            else:
                                if len(str(result)) >= 19:
                                    answers.append({
                                        "type": device_type,
                                        "imei": str(vehicle["imei"]),
                                        "iccid": result[:19],
                                        "monitoring_system": 4,
                                        "vehicleId": vehicle["id"],
                                        "vehicle_name": vehicle["name"],
                                        })

        except (Exception, WialonError, SdkException) as e:
            log.error(f"ошибка в сборщике ответов {e}")
            return []
        else:
            return answers

