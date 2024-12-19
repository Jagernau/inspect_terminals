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
        )
        gl_token = await glonass_class.token()
        if gl_token:
            all_vehicles = await glonass_class.get_all_vehicles_new(
                gl_token, config.GLONASS_PARENT_ID
            )
            if all_vehicles:
                device_types = [item["deviceTypeName"] for item in all_vehicles]
                device_type_counts = Counter(device_types)
                sorted_device_type_counts = dict(
                    sorted(device_type_counts.items(), key=lambda x: x[1], reverse=True)
                )

                async with AsyncSession(config.DB_ENGINE) as session:
                    terminal_db = TerminalDataBase(session)

                    for key in sorted_device_type_counts.keys():
                        for vehicle in all_vehicles:
                            if key == vehicle["deviceTypeName"]:
                                terminal_imei = vehicle["imei"]
                                terminal_in_db = await terminal_db.get_terminal_in_db(terminal_imei)
                                if not terminal_in_db:
                                    #add_terminal_to_db(self, vehicle_data: dict)
                                    pass
                                else:
                                    pass
                                # после определения модели и фирмы
                                # либо по фирме
                                # отправлять команду на терминал
                                # определив из словаря команду
                                command = str()
                                put_command = await glonass_class.put_terminal_comands(
                                        token=gl_token,
                                        sourceid=config.GLONASS_USR_ID,
                                        destinationid=terminal_imei,
                                        taskdata=command,
                                        owner=config.GLONASS_PARENT_ID
                                        )
                                if put_command:
                                   await asyncio.sleep(8)
                                   past_time = datetime.utcnow() - timedelta(minutes=30)
                                   past_time = past_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
                                   future_time = datetime.utcnow() + timedelta(minutes=30)
                                   future_time = future_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
                                   terminal_answer = glonass_class.get_terminal_answer(
                                            token=gl_token,
                                            imei=terminal_imei,
                                            start=past_time, 
                                            end=future_time
                                           )
                                   if terminal_answer:
                                       # сохранить в базе данных
                                       pass
                                



