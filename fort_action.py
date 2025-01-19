from monitoring_systems import fort as ft
from collections import Counter
from my_logger import logger as log
import json
from comands_dict import commands as comm_dict
import asyncio
from config import MONITORING_CONFIG

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
        #try:
        all_vehicles = None
        sorted_device_type_counts = None
        ft_token = await self.fort_class.token()
        if ft_token:
            all_vehicles = await self.fort_class.get_all_vehicles(
                ft_token
            )
            if all_vehicles:
                print(all_vehicles)
        #             device_types = [item['deviceTypeName'] for item in all_vehicles if 'deviceTypeName' in item]
        #             device_type_counts = Counter(device_types)
        #             sorted_device_type_counts = dict(
        #                 sorted(device_type_counts.items(), key=lambda x: x[1], reverse=True))
        #
        # except Exception as e:
        #     log.error(f"Ошибка в получении данных {e}")
        # else:
        #     if all_vehicles and sorted_device_type_counts:
        #         print(sorted_device_type_counts)
        #         return all_vehicles, sorted_device_type_counts
        #     else:
        #         return None

# fort_class = FortAction(
#         MONITORING_CONFIG["fort"]["login"],
#         MONITORING_CONFIG["fort"]["password"],
#         MONITORING_CONFIG["fort"]["address"],
#         )
# asyncio.run(fort_class.get_fort_odjects())


