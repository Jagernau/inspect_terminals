from monitoring_systems import glonasssoft as gl
from collections import Counter
from my_logger import logger as log
from comands_dict import commands as comm_dict
import asyncio
from my_logger import logger as log
import re

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
        self.gl_token = self.glonass_class._token()

    async def get_glonass_odjects(self):
        "Возвращает все объекты, сортированные по количесту типы терминылов"
        try:
            all_vehicles = None
            sorted_device_type_counts = None
            gl_token = self.gl_token
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

    async def put_comands(self, 
                          all_vehicles,
                          sorted_device_type_counts,
                          ):
        "Рассылает команды на терминалы"
        gl_token = self.gl_token
        tasks = []
        for device_type, _ in sorted_device_type_counts.items():
            for vehicle in all_vehicles:
                if 'deviceTypeName' in vehicle and  vehicle['deviceTypeName'] == device_type:
                    terminal_imei = vehicle["imei"]
                    clear_device_type = str(device_type).split(" ")[0]

                    if str(device_type).split(" ")[0] in comm_dict:
                        command = comm_dict[clear_device_type]["iccid"]["command"]
                        tasks.append(asyncio.create_task(self.glonass_class.put_terminal_comands(
                                gl_token=gl_token,
                                destinationid=terminal_imei,
                                taskdata=command
                                )))
        asyncio.gather(*tasks)


    async def answer_objects(self,
                             all_vehicles, 
                             sorted_device_type_counts,
                             ):
        "Собирает ответы с терминалов"
        gl_token = self.gl_token
        answers = []
        try:
            for device_type, _ in sorted_device_type_counts.items():
                for vehicle in all_vehicles:
                    if 'deviceTypeName' in vehicle and vehicle['deviceTypeName'] == device_type:
                        terminal_imei = vehicle["imei"]
                        answer = await self.glonass_class.get_terminal_answer(
                                gl_token=gl_token,
                                imei=terminal_imei,
                                )
                        if answer and len(answer) >= 1:
                            try:
                                matches = []
                                if answer[0]['status'] == True:
                                    raw_answer = answer[0]['answer']
                                    # Извлечение первых 19 цифр, если они есть
                                    pattern = r"(?<!\d)(8\d{17,20})(?!\d)"

                                    matches.extend(re.findall(pattern, str(raw_answer)))
                            except Exception as e:
                                log.error(f"ошибка в приёме и обработке ответа {answer}  {e}")
                                continue
                            else:
                                if len(matches) >=1 and len(matches[0]) >= 19:
                                    answers.append({
                                        "type": str(device_type).split(" ")[0],
                                        "imei": str(terminal_imei),
                                        "iccid": str(matches[0][:19]),
                                        "monitoring_system": 1,
                                        "vehicleId": vehicle["vehicleId"],
                                        "vehicle_name": vehicle["name"],
                                        })

        except Exception as e:
            log.error(f"ошибка в сборщике ответов {e}")
            return []
        else:
            return answers

