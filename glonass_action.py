from monitoring_systems import glonasssoft as gl
from collections import Counter
from my_logger import logger as log
import json

class GlonassAction:
    def __init__(self, 
                 glonass_login,
                 glonass_pass,
                 glonass_adres,
                 glonass_usr_id,
                 glonass_parent_id) -> None:
        self.glonass_class = gl.Glonasssoft(
                 glonass_login,
                 glonass_pass,
                 glonass_adres,
                 glonass_usr_id,
                 glonass_parent_id
                )

    async def get_glonass_odjects(self):
        "Возвращает все объекты, сортированные по количесту типы терминылов"
        try:
            all_vehicles = None
            sorted_device_type_counts = None
            gl_token = await self.glonass_class.token()
            if gl_token:
                all_vehicles = await self.glonass_class.get_all_vehicles_new(
                    gl_token
                )
                if all_vehicles:
                    device_types = [item['deviceTypeName'] for item in all_vehicles if 'deviceTypeName' in item]
                    device_type_counts = Counter(device_types)
                    sorted_device_type_counts = dict(
                        sorted(device_type_counts.items(), key=lambda x: x[1], reverse=True))

        except Exception as e:
            log.error(f"Ошибка в получении данных {e}")
        else:
            if all_vehicles and sorted_device_type_counts:
                return all_vehicles, sorted_device_type_counts
            else:
                return None

    async def put_comands(self, all_vehicles, sorted_device_type_counts):
        "Рассылает команды на терминалы"
        gl_token = await self.glonass_class.token()
        count = 0
        for key in sorted_device_type_counts.keys():
            for vehicle in all_vehicles:
                if key == vehicle['deviceTypeName']:
                    terminal_imei = vehicle["imei"]
                    command = "*?ICCID"
                    await self.glonass_class.put_terminal_comands(
                            gl_token=gl_token,
                            destinationid=terminal_imei,
                            taskdata=command
                            )

                    if count == 20:
                        break
                    count += 1

    async def answer_objects(self, all_vehicles, sorted_device_type_counts):
        "Собирает ответы с терминалов"
        gl_token = await self.glonass_class.token()
        count = 0
        answers = []
        for key in sorted_device_type_counts.keys():
            for vehicle in all_vehicles:
                if key == vehicle['deviceTypeName']:
                    terminal_imei = vehicle["imei"]
                    answer = await self.glonass_class.get_terminal_answer(
                            gl_token=gl_token,
                            imei=terminal_imei,
                            )
                    answers.append({terminal_imei: answer})

                    if count == 20:
                        break
                    count += 1
        return answers

