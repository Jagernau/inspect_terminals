from data_base.db_conectors import MysqlDatabase
from sqlalchemy import update
from data_base import mysql_models_two
import sys
sys.path.append('../')
from inspect_terminals.my_logger import logger



def get_client_info_from_obj(answer_data):
    "Возвращает данные по клиенту по объекту"
    db = MysqlDatabase()
    session = db.session
    try:
        client_info = session.query(
                mysql_models_two.Contragent.ca_id,
                mysql_models_two.Contragent.ca_name,
            ).select_from(mysql_models_two.CaObject).join(
                mysql_models_two.Contragent,
                mysql_models_two.CaObject.contragent_id == mysql_models_two.Contragent.ca_id,
            ).filter(
                mysql_models_two.CaObject.sys_mon_id == answer_data["monitoring_system"],mysql_models_two.CaObject.sys_mon_object_id == answer_data["vehicleId"]).first()
        if client_info:
            return {
                "client_name": client_info.ca_name,
                "client_id": client_info.ca_id,
            }
        else:
            return {
                "client_name": None,
                "client_id": None,
            }
    except Exception as e:
        logger.error(f"Ошибка при получении информации по клиентам: {e}")
        return {
            "client_name": None,
            "client_id": None,
        }
    finally:
        session.close()



def get_availability_sim_in_db(answer_iccid):
    "Возвращает есть ли СИМ ICCID в базе данных, если нет, значит сим клиента"
    db = MysqlDatabase()
    session = db.session
    try:
        iccid_info = session.query(
                mysql_models_two.SimCard.sim_id,
            ).select_from(
                mysql_models_two.SimCard
                ).filter(
                mysql_models_two.SimCard.sim_iccid == str(answer_iccid)
                ).first()
        if iccid_info:
            if iccid_info[0] != None:
                return 1
            else:
                return 0
        else:
            return 0
    except Exception as e:
        logger.error(f"Ошибка при получении информации по СИМ: {e}")
        return 0
    finally:
        session.close()


def get_sim_imei(answer_iccid):
    "Возвращает imei терминала как записанно в бд"
    db = MysqlDatabase()
    session = db.session
    try:
        imei_info = session.query(
                mysql_models_two.SimCard.terminal_imei,
            ).select_from(
                mysql_models_two.SimCard
                ).filter(
                mysql_models_two.SimCard.sim_iccid == str(answer_iccid)
                ).first()
        if imei_info:
            return imei_info[0]
        else:
            return None
    except Exception as e:
        logger.error(f"Ошибка при получении информации по СИМ: {e}")
        return None
    finally:
        session.close()

def update_sim_imei(answer_iccid: str, answer_imei: str):
    "Обновляет данные по сим если не сходятся imei"
    db = MysqlDatabase()
    session = db.session 
    try:      
        sim_info = session.query(
                mysql_models_two.SimCard
            ).filter(
                mysql_models_two.SimCard.sim_iccid == str(answer_iccid),
                ).first()
        session.close()

        if sim_info.terminal_imei == None or sim_info.terminal_imei != str(answer_imei):
            session.execute(
                        update(mysql_models_two.SimCard)
                        .where(
                            mysql_models_two.SimCard.sim_iccid == str(answer_iccid),
                        )
                        .values(terminal_imei=str(answer_imei)))
            session.commit()
            session.close()

            data_log = mysql_models_two.GlobalLogging(
                        section_type="sim_cards", 
                        edit_id=int(sim_info.sim_id),
                        field="terminal_imei",
                        old_value=sim_info.terminal_imei,
                        new_value=answer_imei,
                        sys_id=sim_info.sim_cell_operator,
                        action="update",
                        contragent_id=sim_info.contragent_id
                    )
            session.add(data_log)
            session.commit()
            session.close()

    except Exception as e:
        logger.error(f"Ошибка при обновлении imei {e}")
        session.rollback()
        session.close()


def update_sim_client(sim_iccid: str, sim_client_id: int):
    "Обновляет данные по сим если не сходятся imei"
    db = MysqlDatabase()
    session = db.session
    try:
        sim_info = session.query(
                mysql_models_two.SimCard
            ).select_from(
                mysql_models_two.SimCard
                ).filter(
                mysql_models_two.SimCard.sim_iccid == str(sim_iccid),
                ).first()
        session.close()

        if sim_info.contragent_id == None or sim_info.contragent_id != sim_client_id:
            session.execute(
                        update(mysql_models_two.SimCard)
                        .where(
                            mysql_models_two.SimCard.sim_iccid == sim_iccid,
                        )
                        .values(contragent_id=sim_client_id))
            session.commit()
            session.close()

            data_log = mysql_models_two.GlobalLogging(
                        section_type="sim_cards", 
                        edit_id=int(sim_info.sim_id),
                        field="contragent_id",
                        old_value=sim_info.contragent_id,
                        new_value=sim_client_id,
                        sys_id=sim_info.sim_cell_operator,
                        action="update",
                        contragent_id=sim_client_id
                    )
            session.add(data_log)
            session.commit()
            session.close()

    except Exception as e:
        logger.error(f"Ошибка при обновлении id клиентов у симкарт {e}")
        session.rollback()
        session.close()

def add_inspect_terminal(marge_info):
    "Добавляет проинспектированный терминал в бд"
    db = MysqlDatabase()
    session = db.session
    try:
        data_inspect = mysql_models_two.InspectTerminal(
                type_term = marge_info["type_term"],
                imei = marge_info["imei"],
                iccid = marge_info["iccid"],
                vehicleId = marge_info["vehicleId"],
                vehicle_name = marge_info["vehicle_name"],
                client_name = marge_info["client_name"],
                client_id = marge_info["client_id"],
                iccid_in_db = marge_info["iccid_in_db"],
                if_change_imei = marge_info["if_change_imei"],
                old_sim_imei = marge_info["old_sim_imei"],
                monitoring_system = marge_info["monitoring_system"],

                )
        session.add(data_inspect)
        session.commit()

    except Exception as e:
        logger.error(f"Ошибка при добавлении проинспектированного терминала {e}")
        session.rollback()
    finally:
        session.close()


def get_all_inspected():
    "Возвращает проинспектированные терминалы за последние два месяца"
    db = MysqlDatabase()
    session = db.session
    try:
        inspect_data_info = session.query(
                mysql_models_two.InspectTerminal
            ).select_from(
                mysql_models_two.InspectTerminal
                ).filter(
                mysql_models_two.InspectTerminal.imei != None,
                # Текущий месяц
                ).all()
        if inspect_data_info:
            return inspect_data_info
        else:
            return None
    except Exception as e:
        logger.error(f"Ошибка при получении информации по проинспектированным терминалам: {e}")
        return None
    finally:
        session.close()
