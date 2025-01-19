import threading
from config import MONITORING_CONFIG
from glonass_entry import start_glonass_thread
        
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
