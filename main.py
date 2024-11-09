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

if os.name == 'nt':
    CMD = ctypes.windll.kernel32.GetConsoleWindow()
    ctypes.windll.user32.SetWindowLongW(CMD, -16, ctypes.windll.user32.GetWindowLongW(CMD, -16) | 0x80000)
    ctypes.windll.user32.SetLayeredWindowAttributes(CMD, 0, 235, 0x2)
    os.system('cls')
    print("# github.com/Churkashh")
    time.sleep(0.5)
    os.system('cls')
    

pinneaples_collected = 0
cfg = json.load(open('./config.json', encoding='utf-8')) # чтение конфига


def session(config: dict) -> tls_client.Session:
    """Создание tls-client сессии"""
    session = tls_client.Session(client_identifier='okhttp4_android_13') 
    session.headers = {
            "Accept": "application/json; charset=utf-8",
            "Content-Type": "application/json; charset=UTF-8",
            "Host": "api.ozon.ru",
            "MOBILE-GAID": str(uuid.uuid4()),
            "MOBILE-LAT": "0",
            "User-Agent": "ozonapp_android/17.40.1+2518",
            "x-o3-app-name": "ozonapp_android",
            "x-o3-app-version": config["x-o3-app-version"],
            "x-o3-device-type": "mobile",
            "x-o3-fp": Utils.generate_x_o3(),
            "x-o3-sample-trace": "false"
        }  
        
    session.cookies.set("x-o3-app-name", "ozonapp_android")
    session.cookies.set("__Secure-access-token", config["__Secure-access-token"])
    session.cookies.set("__Secure-refresh-token", config["__Secure-refresh-token"])
    
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
    def sleep_func(account_name: str, error_403=False) -> None:
        """Задержка в софте"""
        if error_403:
            if cfg["Error_handling"]["sleep_if_403_status_code"]:
                sleep_time = random.randint(cfg["Error_handling"]["sleep_time_min"], cfg["Error_handling"]["sleep_time_max"])
                logger.info(f"[{account_name}] [STATUS 403] Аккаунт ушёл в спячку на {sleep_time} минут.")
                time.sleep(sleep_time * 60)
                
            return
        
        if cfg["Sleep_settings"]["sleep_between_pinneaples"]: # Пауза после каждого ананаса
            sleep_time = random.randint(cfg["Sleep_settings"]["min_delay"], cfg["Sleep_settings"]["max_delay"])
            logger.info(f'[{account_name}] Ожидание паузы {sleep_time} секунд.')
            time.sleep(sleep_time)
                            
        if cfg["Sleep_settings"]["afk"]: # Рандомная спячка после сбора
            number = random.randint(1, 100)
            if number <= cfg["Sleep_settings"]["chance_to_afk"]:
                sleep_time = random.randint(cfg["Sleep_settings"]["afk_time_min"], cfg["Sleep_settings"]["afk_time_max"])
                logger.info(f"[{account_name}] Ушел в спячку на {sleep_time} минут.")
                time.sleep(sleep_time * 60)
                                    
    @staticmethod
    def set_title():
        """Название консоли"""
        global pinneaples_collected
        start_time = datetime.now()
        if os.name == 'nt':    
            while True:
                title = f"Фармер Ананасов (github.com/Churkashh) | Используется аккаунтов: {len(cfg["Accounts"])} | Собрано ананасов: {pinneaples_collected} | Времени прошло: {datetime.now() - start_time}"
                ctypes.windll.kernel32.SetConsoleTitleW(title)
                time.sleep(0.2)
                
    
class Ozon():
    def __init__(self, config: dict) -> None:
        self.session = session(config)
        self.account_name = config["account_name"]
        self.config = config
    
    def update_session(self) -> None:
        """Постоянное обновление сессии"""
        while True: 
           self.session = session(self.config)
           time.sleep(10)
    
    def load_cycle(self) -> None:
       """Посещение страницы акции"""
       while True:
           try:
               for i in range(3):
                   self.session.get("https://www.ozon.ru/landing/pineapple?perehod=pineapple_alert")

               break
           except Exception as e:
               logger.warning(f'Исключение: {e}')
               time.sleep(1)
               continue
    
    def get_pinneaple_product(self) -> None:
        """Функция получения товара с ананасом"""
        global pinneaples_collected
        while True:
            try:
                value = random.randint(11111111, 999999999)
                params = {
                    "url": f"/products/{value}/?layout_container=pdppage2copy&layout_page_index=2"
                }
                        
                response = self.session.get("https://api.ozon.ru/composer-api.bx/page/json/v2", params=params)
                if response.status_code == 200:
                    if "hash" in response.text:
                        clean_text = response.text.replace('\\"', '"')
                        payload = {"product_id":Utils.extract(clean_text)[1],"hash_value":Utils.extract(clean_text)[0]}
                        self.collect_pinneaple(payload)
                
                elif response.status_code == 403:
                    logger.error(f'[{self.account_name}] Ошибка при просмотре товара (403) -> возможно невалид куки.')
                    Utils.sleep_func(self.account_name, True)
                    continue
                    
                elif response.status_code == 404:
                    continue
                    
                else:
                    logger.error(f'[{self.account_name}] Неизвестная ошибка просмотра карточки товара ({response.status_code}) -> {response.text}.')   
                    time.sleep(1)
            except Exception as e:
                logger.warning(f"Исключение: {e}")  
                time.sleep(1)   
                continue      
               
    def collect_pinneaple(self, payload: dict) -> None:
        """Сбор ананасов"""
        global pinneaples_collected
        while True:
            try:
                resp = self.session.post("https://api.ozon.ru/composer-api.bx/_action/v2/collapseWidget", json=payload)
                if resp.status_code == 200:
                    pinneaples_collected += 1
                    logger.success(f"[{self.account_name}] Успешно залутал ананас: {resp.json()['data']['notificationBar']['title']}.")
                    Utils.sleep_func(self.account_name)
                
                elif resp.status_code == 403:
                    logger.error(f'[{self.account_name}] Ошибка получения ананаса (403) -> рейтлимит/невалид куки')
                    Utils.sleep_func(self.account_name, True)
                    
                else:
                    logger.error(f'[{self.account_name}] Неизвестная ошибка при получении ананаса ({resp.status_code}) -> {resp.text}')
                    time.sleep(1)

                return
            except Exception as e:
                logger.warning(f"Исключение: {e}")
                time.sleep(1)
                continue
                    
    
def process_account(account: dict):
    """Поток для каждого аккаунта"""
    ozon = Ozon(account)
    threading.Thread(target=ozon.update_session).start()
    ozon.load_cycle()
    ozon.get_pinneaple_product()

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
