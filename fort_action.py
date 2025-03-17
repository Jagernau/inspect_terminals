from monitoring_systems import fort as ft
from collections import Counter
from my_logger import logger as log
import json
from comands_dict import commands as comm_dict
import asyncio
from config import MONITORING_CONFIG
import re
import json

class FortAction:
    def __init__(self, 
                 fort_login,
                 fort_pass,
                 fort_adres,
                 ) -> None:
        self.fort_class = ft.Fort(
                 fort_login,
                 fort_pass,
                 fort_adres,
                )

    async def get_fort_odjects(self):
        "Возвращает все объекты, сортированные по количесту типы терминылов"
        try:
            all_vehicles = None
            ft_token = await self.fort_class.token()
            if ft_token:
                all_vehicles = await self.fort_class.get_all_vehicles(
                    ft_token
            )
        except Exception as e:
            log.error(f"Ошибка в получении данных {e}")
        else:
            if all_vehicles:
                return all_vehicles["objects"]


    async def put_comands(self, 
                          all_vehicles,
                          ):
        "Рассылает команды на терминалы"
        ft_token = await self.fort_class.token()
        tasks = []
        pattern = r"^8\d{13,14}$"
        count = 0
        nex_count = 0
        for vehicle in all_vehicles:
            if re.match(pattern, vehicle["IMEI"]):
                command = comm_dict["NAVTELECOM"]["iccid"]["command"]
                answer = await self.fort_class.put_terminal_comands(
                            token=ft_token,
                            obj_id=vehicle["id"],
                            command=command
                            )
                print(answer)

                count += 1
                if count == 10: break
        for v in all_vehicles:
            command = comm_dict["NAVTELECOM"]["iccid"]["command"]
            result = await self.fort_class.get_terminal_comands(ft_token, v["id"], command)
            print(result)

            nex_count += 1
            if nex_count == 10: break




fort_class = FortAction(
        MONITORING_CONFIG["fort"]["login"],
        MONITORING_CONFIG["fort"]["password"],
        MONITORING_CONFIG["fort"]["address"],
        )
vehicles = asyncio.run(fort_class.get_fort_odjects())
asyncio.run(fort_class.put_comands(vehicles))

