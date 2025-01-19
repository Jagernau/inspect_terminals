from time import sleep
from monitoring_systems import wialon_hosting as wh
from collections import Counter
from my_logger import logger as log
from comands_dict import commands as comm_dict
from my_logger import logger as log
import asyncio
import re
import datetime as dt


class WialonHostingAction:
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

        except Exception as e:
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
                        now = dt.datetime.now(dt.timezone.utc)
                        adjusted_time = now - dt.timedelta(milliseconds=1000)
                        timestamp = int(adjusted_time.timestamp() * 1000)
                        # Время для запроса
                        request_time = timestamp - 300

                        answer = self.wialon_hosting_class.get_last_masseges_data(
                                obj_id=terminal_id,
                                curent_time=request_time
                                )
                        print(answer) 
                        # if answer and len(answer) >= 1:
                        #     try:
                        #         digits = ""
                        #         if answer[0]['status'] == True:
                        #             raw_answer = answer[0]['answer']
                        #             # Извлечение первых 19 цифр, если они есть
                        #             digits = ''.join(filter(str.isdigit, raw_answer))
                        #     except Exception as e:
                        #         log.error(f"ошибка в приёме и обработке ответа {answer}  {e}")
                        #         continue
                        #     else:
                        #         if len(digits) >= 19:
                        #             answers.append({
                        #                 "type": str(device_type).split(" ")[0],
                        #                 "imei": str(terminal_imei),
                        #                 "iccid": str(digits[:19]),
                        #                 "monitoring_system": 1,
                        #                 "vehicleId": vehicle["vehicleId"],
                        #                 "vehicle_name": vehicle["name"],
                        #                 })

        except Exception as e:
            log.error(f"ошибка в сборщике ответов {e}")
            return []
        else:
            return answers

