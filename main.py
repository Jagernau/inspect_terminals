# file: main.py

import asyncio
import threading
from glonass_action import GlonassAction
# from data_base.crud import save_answers_to_db, save_command_status_to_db
from config import MONITORING_CONFIG
from my_logger import logger as log

async def process_glonass_system(config):
    """
    Обрабатывает работу с системой мониторинга ГЛОНАСС.
    """
    glonass_action = GlonassAction(
        glonass_login=config["login"],
        glonass_pass=config["password"],
        glonass_adres=config["address"],
        glonass_usr_id=config["user_id"],
        glonass_parent_id=config["parent_id"],
    )

    try:
        # Получение объектов
        all_vehicles, sorted_device_type_counts = await glonass_action.get_glonass_odjects()
        if all_vehicles:
            # Рассылка команд
            await glonass_action.put_comands(all_vehicles, sorted_device_type_counts)
            await asyncio.sleep(10)

            # Сбор ответов
            answers = await glonass_action.answer_objects(all_vehicles, sorted_device_type_counts)
            for anwer in answers:
                marge_full_info = anwer
                # _ type Str тип терминала
                # _ imei Str imei терминала
                # _ iccid Str iccid Сим карты
                # _ monitoring_sustem Int Система мониторинга 
                # _ vehicleId Str Ид в системе мониторинга
                # _ vehicle_name Str Имя объекта
                # + client_name Str Имя клиента
                # + client_id Int Ид клиента в бд
                # + iccid_in_db Bool Наличие сим в бд
                # + if_change_iccid Bool Изменится ли imei у СИМ
                # + old_sim_imei Str Если произошли изменения в Сим, старый
                # + datetime Авто время изменения

            log.info(answers)
    except Exception as e:
        log.error(f"Ошибка при работе с ГЛОНАСС: {e}")

def start_glonass_thread(config):
    """
    Запускает отдельный поток для обработки ГЛОНАСС.
    """
    asyncio.run(process_glonass_system(config))

def main():
    """
    Основной метод запуска программы.
    """
    threads = []

    for system_name, system_config in MONITORING_CONFIG.items():
        if system_name == "glonass":
            thread = threading.Thread(target=start_glonass_thread, args=(system_config,))
            threads.append(thread)
            thread.start()

    # Ожидание завершения всех потоков
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()

