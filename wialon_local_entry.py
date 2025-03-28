import asyncio
from wialon_local_action import WialonLocalAction
from data_base import crud
from my_logger import logger as log
from time import sleep
from wialon.sdk import WialonError, SdkException


def chunk_list(data, chunk_size):
    """
    Разделяет список на чанки заданного размера.
    
    :param data: Исходный список.
    :param chunk_size: Размер каждого чанка.
    :return: Список чанков.
    """
    return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]


async def process_wialon_local_system(config):
    """
    Обрабатывает работу с системой мониторинга Wialon Local.
    """
    wialon_hosting_action = WialonLocalAction(
        wialon_hosting_token=config["wialon_local_token"],
        wialon_hosting_adres=config["address"],
    )
    
    # Получение объектов
    all_vehicles, sorted_device_type_counts = await wialon_hosting_action.get_wialon_hosting_odjects()
    if all_vehicles:
        all_inspects_in_db = crud.get_all_inspected()
        if all_inspects_in_db:
            all_inspects_imei = set(vehicle_db.imei for vehicle_db in all_inspects_in_db)
            new_vehicles_len = [vehicle for vehicle in all_vehicles if vehicle["imei"] not in all_inspects_imei]
        else:
            new_vehicles_len = all_vehicles

        chunked_vehicles = chunk_list(new_vehicles_len, 20)
        for chunk in chunked_vehicles:
            try:
                
                # Рассылка команд
                wialon_hosting_action.put_comands(chunk, sorted_device_type_counts)
                await asyncio.sleep(10)

                # Сбор ответов
                answers = wialon_hosting_action.answer_objects(chunk, sorted_device_type_counts)

                if len(answers) >= 1:
                    for answer in answers:
                        if answer["monitoring_system"] and answer["vehicleId"]:
                            try:
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
                                    if client_info["client_id"] == None:
                                        log.error(f"ТС {answer.get('vehicle_name')} не привязанна к клиенту")
                                    else:
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

                            except Exception as e:
                                log.error(f"Ошибка при форировании записи инспекции под БД: {e}")
                                continue
                            else:
                                if marge_full_info["client_id"] != None:
                                    crud.add_inspect_terminal(marge_full_info)
                                log.info(marge_full_info)
            except (Exception, WialonError, SdkException) as e:
                log.error(f"Ошибка при работе с Wialon_Local: {e}")
                continue

def start_wialon_local_thread(config):
    """
    Запускает отдельный поток для обработки Виалон Локал.
    """
    while True:
        asyncio.run(process_wialon_local_system(config))
        sleep(10)

