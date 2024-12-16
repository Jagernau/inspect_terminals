from sqlalchemy import update
from sqlalchemy.orm import Session
from data_base import mysql_models_two
from data_base.db_conectors import MysqlDatabaseTwo 
from inspect_terminals.my_logger import logger


class SimDataBase:
    """Класс для работы с СИМ."""

    def __init__(self):
        self.db = MysqlDatabaseTwo()

    def _execute_query(self, query_func):
        """Общий метод для выполнения запросов."""
        session = self.db.session
        try:
            result = query_func(session)
            session.commit()
            return result
        except Exception as e:
            logger.error(f"Ошибка при выполнении запроса: {e}")
            session.rollback()
            return None
        finally:
            session.close()

    def update_sim_imei(self, sim_iccid, term_imei):
        """
        Обновляет СИМ imei
        """
        def query(session: Session):
            return session.execute(
                update(mysql_models_two.SimCard)
                .where(
                    mysql_models_two.SimCard.sim_iccid == sim_iccid,
                    mysql_models_two.SimCard.terminal_imei != term_imei
                )
                .values(terminal_imei=term_imei)
            )
        self._execute_query(query)

    def update_sim_contragent(self, sim_iccid, contragent_id):
        """
        Обновляет СИМ Контрагентов
        """
        def query(session: Session):
            return session.execute(
                update(mysql_models_two.SimCard)
                .where(
                    mysql_models_two.SimCard.sim_iccid == sim_iccid,
                    mysql_models_two.SimCard.contragent_id != contragent_id
                )
                .values(contragent_id=contragent_id)
            )
        self._execute_query(query)



class TerminalDataBase:
    """Класс для работы с Терминалами."""

    def __init__(self):
        self.db = MysqlDatabaseTwo()

    def _execute_query(self, query_func):
        """Общий метод для выполнения запросов."""
        session = self.db.session
        try:
            result = query_func(session)
            session.commit()
            return result
        except Exception as e:
            logger.error(f"Ошибка при выполнении запроса: {e}")
            session.rollback()
            return None
        finally:
            session.close()


    def update_term_contragent(self, term_imei, contragent_id):
        """
        Обновляет СИМ Контрагентов
        """
        def query(session: Session):
            return session.execute(
                update(mysql_models_two.Device)
                .where(
                    mysql_models_two.Device.device_imei == term_imei,
                    mysql_models_two.Device.contragent_id != contragent_id
                )
                .values(contragent_id=contragent_id)
            )
        self._execute_query(query)

    def add_terminal(self, term_imei, contragent_id, term_type):
        pass
