# github.com/Churkashh

import re
import os
import time
import json
import uuid
import string
import random
import ctypes
import threading
import tls_client

from loguru import logger
from datetime import datetime

os.system('cls')
CMD = ctypes.windll.kernel32.GetConsoleWindow()
ctypes.windll.user32.SetWindowLongW(CMD, -16, ctypes.windll.user32.GetWindowLongW(CMD, -16) | 0x80000)
ctypes.windll.user32.SetLayeredWindowAttributes(CMD, 0, 235, 0x2)
if os.name == "nt":
    print("# github.com/Churkashh")
    time.sleep(0.5)
    os.system('cls')

pinneaples_collected = 0
cfg = json.load(open('./config.json', encoding='utf-8')) # чтение конфига


def session(config: dict):
    """Создание tls-client сессии"""
    session = tls_client.Session(client_identifier='okhttp4_android_13') 
    session.headers = {
        "Accept": "application/json; charset=utf-8",
        "Content-Type": "application/json; charset=UTF-8",
        "Host": "api.ozon.ru",
        "MOBILE-GAID": str(uuid.uuid4()),
        "MOBILE-LAT": "0",
        "User-Agent": "ozonapp_android/17.40.1+2517",
        "x-o3-app-name": "ozonapp_android",
        "x-o3-app-version": config["x-o3-app-version"],
        "x-o3-device-type": "mobile",
        "x-o3-fp": Utils.generate_x_o3(),
        "x-o3-sample-trace": "false"
    }  
    
    session.cookies.set("__Secure-access-token", config["__Secure-access-token"])
    session.cookies.set("__Secure-refresh-token", config["__Secure-refresh-token"])
    session.cookies.set("abt_data", config["abt_data"])
    session.cookies.set("x-o3-app-name", "ozonapp_android")
    
    if config["use_proxy"]:
        session.proxies = f"http://{config["proxy"]}"
    
    return session


class Utils():
    @staticmethod
    def generate_x_o3() -> str: # Генерация x-o3-fp заголовка
        return f"1.{''.join(random.choices(string.hexdigits[:16].lower(), k=16))}"
    
    @staticmethod
    def extract(text: str):
        return re.search(r'"hash_value":"(\d+)"', text).group(1), re.search(r'"product_id":"(\d+)"', text).group(1)
    
    @staticmethod
    def set_title(): # Установка названия консоли
        global pinneaples_collected
        start_time = datetime.now()
        while True:
            if os.name == "nt":
                title = f"Фармер Ананасов (github.com/Churkashh) | Используется аккаунтов: {len(cfg["Accounts"])} | Собрано ананасов: {pinneaples_collected} | Времени прошло: {datetime.now() - start_time}"
                ctypes.windll.kernel32.SetConsoleTitleW(title)
                time.sleep(0.2)
                
    
class Ozon():
    def __init__(self, config: dict) -> None:
        self.session = session(config)
        self.account_name = config["account_name"]
        
    def start(self):
       while True:
           try:
               for i in range(3):
                   self.session.get("https://www.ozon.ru/landing/pineapple/?__rr=1")
               
               break
           except Exception as e:
               print(e)
               continue
    
    def farm_pinneaple(self):
        """Основная функция фарма ананасов"""
        global pinneaples_collected
        while True:
            try:
                value = random.randint(11111111, 999999999)
                params = {
                    "url": f"/products/{value}/?avtc=1&avte=4&avts=1730880275&layout_container=pdppage2copy&layout_page_index=2&sh=mc8W2I8izg&start_page_id=8b6f3cc9bc873a84f9dc289e0434c615"
                }
                        
                response = self.session.get("https://api.ozon.ru/composer-api.bx/page/json/v2", params=params)
                if response.status_code == 200:
                    if "hash" in response.text:
                        clean_text = response.text.replace('\\"', '"')
                
                        payload = {"product_id":Utils.extract(clean_text)[1],"hash_value":Utils.extract(clean_text)[0]}
                        resp = self.session.post("https://api.ozon.ru/composer-api.bx/_action/v2/collapseWidget", json=payload)
                        if resp.status_code == 200:
                            pinneaples_collected += 1
                            logger.success(f"[{self.account_name}] Успешно залутал ананас: {resp.json()['data']['notificationBar']['title']}.")
                            
                            if cfg["Pinneaples"]["sleep_between_pinneaples"]: # Пауза после каждого ананаса
                                sleep_time = random.randint(cfg["Pinneaples"]["min_delay"], cfg["Pinneaples"]["max_delay"])
                                logger.info(f'[{self.account_name}] Ожидание паузы {sleep_time} секунд.')
                                time.sleep(sleep_time)
                            
                            if cfg["Pinneaples"]["afk"]: # Рандомная спячка после сбора
                                number = random.randint(1, 100)
                                if number <= cfg["Pinneaples"]["chance_to_afk"]:
                                    sleep_time = random.randint(cfg["Pinneaples"]["afk_time_min"], cfg["Pinneaples"]["afk_time_max"])
                                    logger.info(f"[{self.account_name}] Ушел в спячку на {sleep_time} минут.")
                                    time.sleep(sleep_time * 60)
                            
                        else:
                            logger.error(f"[{self.account_name}] Ошибка получения ананаса ({resp.status_code}) -> {resp.text}")
                
                elif response.status_code == 403:
                    logger.error(f'[{self.account_name}] Ошибка ({response.status_code}) -> возможно невалид куки.')
                    continue
                    
                elif response.status_code == 404:
                    continue
                    
                else:
                    logger.error(f'[{self.account_name}] Неизвестная ошибка просмотре карточки товара ({resp.status_code}) -> {resp.text}.')   
                    time.sleep(1)

            except Exception as e:
                logger.warning(f"Исключение: {e}")     
                continue      
            
    
def process_account(account: dict):
    """Поток для каждого аккаунта"""
    ozon = Ozon(account)
    ozon.start()
    ozon.farm_pinneaple()

def main():
    """Фукнция запуска"""
    try:
        threading.Thread(target=Utils.set_title).start()
        threads = []
        for account in cfg["Accounts"]:
            thread = threading.Thread(target=process_account, args=(account,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

    except Exception as e:
        logger.warning(f"Исключение: {e}")


if __name__ == "__main__":
    main()
    
# github.com/Churkashh