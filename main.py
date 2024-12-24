from monitoring_systems import glonasssoft as gl
import config
from collections import Counter
import asyncio
from data_base.crud import TerminalDataBase
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

async def get_glonass_commands():
    if config.GLONASS_LOGIN and config.GLONASS_PASS and config.GLONASS_BASED_ADRESS and config.GLONASS_PARENT_ID:
        glonass_class = gl.Glonasssoft(
            login=config.GLONASS_LOGIN,
            password=config.GLONASS_PASS,
            based_adres=config.GLONASS_BASED_ADRESS,
            glonass_user_id=config.GLONASS_USR_ID,
            glonass_parent_id=config.GLONASS_PARENT_ID
        )
        gl_token = await glonass_class.token()
        if gl_token:
            all_vehicles = await glonass_class.get_all_vehicles_new(
                gl_token
            )
            if all_vehicles:
                device_types = [item["deviceTypeName"] for item in all_vehicles]
                device_type_counts = Counter(device_types)
                sorted_device_type_counts = dict(
                    sorted(device_type_counts.items(), key=lambda x: x[1], reverse=True)
                )

                count = 0
                for key in sorted_device_type_counts.keys():
                    for vehicle in all_vehicles:
                        if key == vehicle["deviceTypeName"]:
                            terminal_imei = vehicle["imei"]
                            # async with AsyncSession(config.DB_ENGINE) as session:
                            #     terminal_db = TerminalDataBase(session)
                            #     terminal_in_db = await terminal_db.get_terminal_in_db(terminal_imei)
                            # if not terminal_in_db:
                            #     #add_terminal_to_db(self, vehicle_data: dict)
                            #     pass
                            # else:
                            #     pass
                            command = "*?ICCID"
                            glonass_class.action_glonass(
                                    )
                                



if __name__ == "__main__":
    # Запуск асинхронной программы
    asyncio.run(get_glonass_commands())

