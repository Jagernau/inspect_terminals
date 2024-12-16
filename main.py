import time
from datetime import datetime
from my_logger import logger
from data_base import crud
from monitoring_systems import glonasssoft as gl
import config
import json
from collections import Counter

def get_glonass_vehic():
    glonass_class = gl.Glonasssoft(login=config.GLONASS_LOGIN,
                             password=config.GLONASS_PASS, 
                             based_adres=config.GLONASS_BASED_ADRESS
                             )
    gl_token = glonass_class.token()
    all_vehicles = glonass_class.get_all_vehicles_new(
            gl_token,
            config.GLONASS_PARENT_ID
            )
    if all_vehicles:
        device_types = [item["deviceTypeName"] for item in all_vehicles]
        device_type_counts = Counter(device_types)
        sorted_device_type_counts = dict(sorted(device_type_counts.items(), key=lambda x: x[1], reverse=True))
        print(sorted_device_type_counts)


    # with open("all_vh_gl.json", "w", encoding='utf-8') as file:
    #     json.dump(all_vehicles, file, ensure_ascii=False, indent=2)

    
get_glonass_vehic()
