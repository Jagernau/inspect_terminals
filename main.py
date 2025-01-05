import asyncio
import threading
from glonass_action import GlonassAction
from data_base import crud
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
            all_inspects_in_db = crud.get_all_inspected()
            if all_inspects_in_db:
                all_inspects_imei = set(vehicle_db.imei for vehicle_db in all_inspects_in_db)
                new_vehicles_len = [vehicle for vehicle in all_vehicles if vehicle["imei"] not in all_inspects_imei]
            else:
                new_vehicles_len = all_vehicles
            # Рассылка команд
            await glonass_action.put_comands(new_vehicles_len, sorted_device_type_counts)
            await asyncio.sleep(10)

            # Сбор ответов
            answers = await glonass_action.answer_objects(new_vehicles_len, sorted_device_type_counts)
            if len(answers) >= 1:
                for answer in answers:
                    if answer["monitoring_system"] and answer["vehicleId"]:
                        client_info = crud.get_client_info_from_obj({
                            "monitoring_system": answer.get("monitoring_system"),
                            "vehicleId": answer.get("vehicleId"),
                        })
                        availability_sim_in_db = crud.get_availability_sim_in_db(
                                answer.get("iccid")
                                )
                        if_change_imei = 0
                        old_sim_imei = None
                        if availability_sim_in_db == 1:
                            sim_db_imei = crud.get_sim_imei(answer.get("iccid"))
                            old_sim_imei = sim_db_imei
                            crud.update_sim_client(
                                    sim_iccid=answer.get("iccid"),
                                    sim_client_id=int(client_info["client_id"])
                                    )
                            if sim_db_imei != answer.get("imei"):
                                if_change_imei = 1
                                crud.update_sim_imei(
                                        answer_iccid=str(answer["iccid"]),
                                        answer_imei=str(answer["imei"])
                                        )
                        
                        marge_full_info = {
                            "type_term": answer["type"],
                            "imei": answer["imei"],
                            "iccid": answer["iccid"],
                            "monitoring_system": answer["monitoring_system"],
                            "vehicleId": answer.get("vehicleId"),
                            "vehicle_name": answer.get("vehicle_name"),
                            "client_name": client_info.get("client_name"),
                            "client_id": client_info.get("client_id"),
                            "iccid_in_db": availability_sim_in_db,
                            "if_change_imei": if_change_imei,# Изменяется ли imei
                            "old_sim_imei": old_sim_imei,# imei SIM до изменений
                        }
                        crud.add_inspect_terminal(marge_full_info)
                        log.info(marge_full_info)
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

