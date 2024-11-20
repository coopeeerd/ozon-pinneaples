# github.com/Churkashh
VERSION = 1.08

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
from bs4 import BeautifulSoup

if os.name == "nt":
    CMD = ctypes.windll.kernel32.GetConsoleWindow()
    ctypes.windll.user32.SetWindowLongW(CMD, -16, ctypes.windll.user32.GetWindowLongW(CMD, -16) | 0x80000)
    ctypes.windll.user32.SetLayeredWindowAttributes(CMD, 0, 235, 0x2)
    os.system("cls")
    print("# github.com/Churkashh")
    time.sleep(0.5)
    os.system("cls")
    
products_checked = 0
pinneaples_collected = 0
cfg = json.load(open("./config.json", encoding="utf-8")) # чтение конфига


def session(config: dict) -> tls_client.Session:
    """Создание tls-client сессии"""
    session = tls_client.Session(client_identifier="okhttp4_android_13", random_tls_extension_order=True) 
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
    if config["abt_data"]:
        session.cookies.set("abt_data", config["abt_data"])
        
    if config["use_proxy"]:
        session.proxies = f"http://{config["proxy"]}"
    
    return session


class Utils():
    @staticmethod
    def generate_x_o3() -> str: 
        """Генерация x-o3-fp заголовка"""
        return f"1.{''.join(random.choices(string.hexdigits[:16].lower(), k=16))}"
    
    @staticmethod
    def generate_abt_data(prefix="7.") -> str:
        """Генерация рандом abt_data"""
        length = random.randint(475, 520)
        return prefix + ''.join(random.choice(string.ascii_letters + string.digits + "-_") for _ in range(length))
    
    @staticmethod
    def extract(text: str):
        """Получение значений для получения ананаса"""
        return re.search(r'"hash_value":"(\d+)"', text).group(1), re.search(r'"product_id":"(\d+)"', text).group(1)
    
    @staticmethod
    def sleep_func(account_name: str, error_403=False) -> None:
        """Задержка в софте"""
        if error_403:
            if cfg["Error_handling"]["sleep_if_403_status_code"]: # Спячка в случае статус кода 403 при получении ананаса
                sleep_time = random.randint(cfg["Error_handling"]["sleep_time_min"], cfg["Error_handling"]["sleep_time_max"])
                logger.info(f"[{account_name}] [STATUS 403] Аккаунт ушёл в спячку на {sleep_time} минут.")
                time.sleep(sleep_time * 60)
                
            return
        
        if cfg["Sleep_settings"]["sleep_between_pinneaples"]: # Пауза после каждого ананаса
            sleep_time = random.randint(cfg["Sleep_settings"]["min_delay"], cfg["Sleep_settings"]["max_delay"])
            logger.info(f"[{account_name}] Ожидание паузы {sleep_time} секунд.")
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
        global pinneaples_collected, products_checked
        start_time = datetime.now()
        if os.name == "nt":    
            while True:
                title = f"v{VERSION} Фармер Ананасов (github.com/Churkashh) | Используется аккаунтов: {len(cfg["Accounts"])} | Собрано ананасов: {pinneaples_collected} | Товаров просмотрено: {products_checked} | Времени прошло: {datetime.now() - start_time}"
                ctypes.windll.kernel32.SetConsoleTitleW(title)
                time.sleep(0.2)
                
    
class Ozon():
    def __init__(self, config: dict) -> None:
        self.session = session(config)
        self.account_name = config["account_name"]
        self.config = config
        self.product_check_tries = 0
        self.pinneaples_collected = 0
        
    def reset_product_check_tries(self) -> None:
        """Сбрасывает счётчик неудачных попыток просмотра товара"""
        while True:
            self.product_check_tries = 0
            time.sleep(1800)
            
    def update_abt_data(self) -> None:
        """Постоянно обновляет abt_data"""
        if self.config["generate_abt_data"]:
            while True:
                self.session.cookies.set("abt_data", Utils.generate_abt_data())
                time.sleep(30)
    
    def load_cycle(self) -> None:
        """Посещение страницы акции и получение количества ананасов аккаунта"""
        tries = 0
        while True:
            try:
                for _ in range(3):
                    resp = self.session.get("https://www.ozon.ru/landing/pineapple/?__rr=1")
                    
                soup = BeautifulSoup(resp.text, 'html.parser')
                
                pinneaple_tag = soup.find(class_="zp7_29")
                if pinneaple_tag:
                    self.pinneaples = int(pinneaple_tag.get_text())
                    logger.info(f"[{self.account_name}] Ананасов на аккаунте: {self.pinneaples}")
                    
                else:
                    tries += 1
                    if tries > 5:   
                        logger.error(f"[{self.account_name}] Не удалось посетить страницу ананасов ({resp.status_code}) -> куки невалид.")   
                        self.stop_thread() 
                    self.session = session(self.config)
                    continue

                break
            except Exception as e:
                logger.warning(f"Исключение: {e}")
                time.sleep(1)
    
    def get_pinneaple_product(self) -> None:
        """Функция получения товара с ананасом"""
        global pinneaples_collected, products_checked
        while True:
            try:
                if self.product_check_tries >= cfg["Error_handling"]["max_product_check_tries"]: # Проверка количества неуспешных попыток посмотреть карточку товара
                    logger.error(f"[{self.account_name}] [MAX_CHECK_TRIES] Лимит просмотра товара превышен.")
                    self.stop_thread()
                    
                value = random.randint(11111111, 999999999)
                params = {
                    "url": f"/products/{value}/?layout_container=pdppage2copy&layout_page_index=2"
                }
                        
                response = self.session.get("https://api.ozon.ru/composer-api.bx/page/json/v2", params=params)
                if response.status_code == 200:
                    products_checked += 1
                    if "hash" in response.text:
                        clean_text = response.text.replace('\\"', '"')
                        payload = {"product_id":Utils.extract(clean_text)[1],"hash_value":Utils.extract(clean_text)[0]}
                        self.collect_pinneaple(payload)
                    
                    else:
                        if cfg["Sleep_settings"]["sleep_between_products"]:
                            sleep_time = random.uniform(cfg["Sleep_settings"]["min_time"], cfg["Sleep_settings"]["max_time"])
                            time.sleep(sleep_time)
                
                elif response.status_code == 403:
                    self.product_check_tries += 1
                    logger.error(f"[{self.account_name}] Ошибка при просмотре товара (403) -> возможно невалид куки.")
                    self.session = session(self.config)
                    continue
                    
                elif response.status_code == 404:
                    continue
                    
                else:
                    logger.error(f"[{self.account_name}] Неизвестная ошибка просмотра карточки товара ({response.status_code}) -> {response.text}.")   
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
                    self.pinneaples_collected += 1
                    if "2" in resp.text:
                        pinneaples_collected += 1
                        self.pinneaples_collected += 1
                    
                    logger.success(f"[{self.account_name}] Успешно залутал ананас: {resp.json()["data"]["notificationBar"]["title"]}. | Собрано: {self.pinneaples_collected}")
                    Utils.sleep_func(self.account_name)
                
                elif resp.status_code == 403:
                    logger.error(f"[{self.account_name}] Ошибка получения ананаса (403) -> рейтлимит/невалид куки")
                    Utils.sleep_func(self.account_name, True)
                    
                else:
                    logger.error(f"[{self.account_name}] Неизвестная ошибка при получении ананаса ({resp.status_code}) -> {resp.text}")
                    time.sleep(1)

                return
            except Exception as e:
                logger.warning(f"Исключение: {e}")
                time.sleep(1)
                continue
            
            
    def stop_thread(self) -> None:
        """Бесконечный цикл (завершение потока)"""
        try:
            logger.info(f"[{self.account_name}] Завершаю поток... | Собрано: {self.pinneaples_collected}")
            while True:
                time.sleep(0.02)
                pass
        except Exception as e:
            logger.warning(f"Исключение: {e}")
            time.sleep(1)
            self.stop_thread()
                    
    
def process_account(account: dict):
    """Поток для каждого аккаунта"""
    logger.info(f"[{account["account_name"]}] Запускаю поток...")
    ozon = Ozon(account)
    threading.Thread(target=ozon.reset_product_check_tries).start()
    threading.Thread(target=ozon.update_abt_data).start()
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
