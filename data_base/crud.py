from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, insert
from data_base import mysql_models_two
from sqlalchemy.orm import joinedload
from inspect_terminals.my_logger import logger

class SimDataBase:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def update_sim_imei(self, sim_iccid, term_imei):
        """Асинхронное обновление IMEI SIM-карты"""
        try:
            query = (
                update(mysql_models_two.SimCard)
                .where(
                    mysql_models_two.SimCard.sim_iccid == sim_iccid,
                    mysql_models_two.SimCard.terminal_imei != term_imei,
                )
                .values(terminal_imei=term_imei)
            )
            await self.session.execute(query)
            await self.session.commit()
        except Exception as e:
            logger.error(f"Ошибка при обновлении SIM-карты: {e}")
            await self.session.rollback()

class TerminalDataBase:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def update_term_contragent(self, term_imei, contragent_id):
        """Асинхронное обновление контрагентов терминалов"""
        try:
            query = (
                update(mysql_models_two.Device)
                .where(
                    mysql_models_two.Device.device_imei == term_imei,
                    mysql_models_two.Device.contragent_id != contragent_id,
                )
                .values(contragent_id=contragent_id)
            )
            await self.session.execute(query)
            await self.session.commit()
        except Exception as e:
            logger.error(f"Ошибка при обновлении терминала: {e}")
            await self.session.rollback()


    async def get_terminal_in_db(self, term_imei: str):
        """Асинхронный метод для получения терминала и его модели из БД по IMEI."""
        try:
            # Выполняем join между Device и DevicesBrand
            query = (
                select(
                    mysql_models_two.Device.device_serial,
                    mysql_models_two.Device.device_imei,
                    mysql_models_two.DevicesBrand.name.label("model_name"),
                )
                .join(
                    mysql_models_two.DevicesBrand,
                    mysql_models_two.Device.devices_brand_id == mysql_models_two.DevicesBrand.id,
                )
                .where(mysql_models_two.Device.device_imei == term_imei)
            )
            result = await self.session.execute(query)
            terminal = result.fetchone()

            # Если терминал найден, возвращаем данные
            if terminal:
                return {
                    "device_serial": terminal.device_serial,
                    "device_imei": terminal.device_imei,
                    "model_name": terminal.model_name,
                }
            return None
        except Exception as e:
            logger.error(f"Ошибка при получении терминала из базы: {e}")
            return None


    async def add_terminal_to_db(self, vehicle_data: dict):
        """Асинхронное добавление нового терминала в базу данных."""
        try:
            query = insert(mysql_models_two.Device).values(
                device_serial=vehicle_data["serialNumber"], #нет пока
                device_imei=vehicle_data["imei"],
                devices_brand_id=vehicle_data.get("deviceBrandId"), #нет пока
                terminal_date=vehicle_data.get("terminalDate"), # нет пока
                client_name=vehicle_data.get("clientName", "Неизвестный клиент"), # нет пока
                # дополнить
            )
            await self.session.execute(query)
            await self.session.commit()
            logger.info(f"Терминал с IMEI {vehicle_data['imei']} добавлен в базу данных.")
        except Exception as e:
            logger.error(f"Ошибка при добавлении терминала: {e}")
            await self.session.rollback()

