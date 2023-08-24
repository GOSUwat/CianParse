import os
import json
import logging

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, filename="py_log.log",filemode="w",format="%(asctime)s %(levelname)s %(message)s")

class Driver:
    """Создает и возвращает драйвер"""

    def __init__(self):
        service = Service()
        options = webdriver.ChromeOptions()
        self.driver = webdriver.Chrome(service=service,options=options)
        self.driver.maximize_window()
        logging.info("Driver init done")

    @property
    def get_driver(self) -> webdriver:
        """
        Возвращает webdriver
        Returns:
            webdriver: Экземпляр webdriver
        """
        return self.driver


class Urls:
    """ Создает и модифицирует ссылки """
    @property
    def get_urls(self) -> list[str]:
        """ Читает файл и получает список ссылок
        Returns:
            list[str]: Список ссылок
        """
        str_urls = ""
        with open("urls.ini", "r", encoding="utf-8") as file:
            str_urls = file.read()
            file.close()
        urls = str_urls.split("\n")
        if "" in urls:
            urls.remove("")
        logging.info("get_urls complete")
        return urls

    def write_url(self, url):
        """ Добавляет пройденнные ссылки в файл """
        with open("urls.ini", "a", encoding="utf-8") as file:
            file.write(url+"\n")
            file.close()
        logging.info("write_url complete")

    def clear_urls(self):
        """ Очищает файл от ссылок """
        with open("urls.ini", "w", encoding="utf-8") as file:
            file.write("")
            file.close()
        logging.info("clear_urls complete")


class Parsing:
    """ Процесс сбора и обработки данных парсера """

    def __init__(self):
        driver_ = Driver()
        self.driver = driver_.get_driver
        self.url_list = []
        self.data = ""
        self.url = ""

    def get_source(self, url):
        """ Получение html страницы по ссылке """
        logging.info(f"get_source url: {url}") 
        # Открытие ссылки
        try:
            urls = Urls()
            self.driver.get(url)
            self.url = str(self.driver.current_url)
        except Exception as exception:
            logging.exception(f"driver get url: {exception}")
            self.stop()
        else:
            logging.info(f"driver get_source done.")
        try:
            # Если парсер прошел все страницы
            if self.url in self.url_list:
                urls.clear_urls()
                logging.info(f"parsing done. Closing parser.")
                self.stop()
            else:
                self.url_list = ur.get_urls
                self.data = self.driver.page_source
        except Exception as exception:
            logging.exception(f"data exception: {exception}")         
        finally:
            # Обработка временного файла с данными
            self.get_items(self.page_number(self.url))
            logging.info(f"get items complete")
    
    @staticmethod
    def error_handler(func):
        def handler(*args, **kwargs):
            try:
                res = func(*args, **kwargs)
            except Exception as exception:
                logging.exception(f"{func.__name__} exception: {exception}")
            else:
                logging.info(f"{func.__name__} done.")
                return res
        return handler
    
    @error_handler
    def find_article(self,soup):
        # Ищем все блоки article
        item_divs = soup.find_all("article")
        return item_divs
    
    @error_handler
    def find_href(self,item):
        item_href = item.find(
                    "a", class_="_93444fe79c--media--9P6wN").get("href")
        return item_href
    
    @error_handler
    def find_header(self,item):
        header = item.find(
                    "span", attrs={"data-mark": "OfferTitle"}).find("span").text
        return header
    
    @error_handler
    def find_sepNames(self,item):
        sep_names = item.find_all(
                    "a", class_="_93444fe79c--link--NQlVc")
        return sep_names
    
    @error_handler
    def create_name(self,sep_names):
        addr = ""
        for name in sep_names:
            addr += f" {name.contents[0]}"
        return addr
    
    @error_handler
    def find_price(self,item):
        price = item.find(
            "span", attrs={"data-mark": "MainPrice"}).find("span").text
        return price
    
    @error_handler
    def find_content(self,item):
        content = item.find(
                    "div", attrs={"data-name": "Description"}).find("p").text
        return content
    
    @error_handler
    def find_devName(self,item):
        dev = item.find("div",
                    class_="_93444fe79c--name-container--enElO").find("span").text
        return dev
    
    @error_handler
    def create_dic(self,item,page_number):
        new_data = {
                    "Заголовок": self.find_href(item),
                    "Ссылка": self.find_header(item),
                    "Адрес": self.create_name(self.find_sepNames(item)),
                    "Цена": self.find_price(item),
                    "Описание": self.find_content(item),
                    "Застройщик": self.find_devName(item),
                    "Номер страницы": page_number
                }
        return new_data
    
    @error_handler  
    def append_data(self,data_list):
        with open("file.json", "a", encoding="utf-8") as json_:
                json.dump(data_list, json_, indent=5, ensure_ascii=False)
                
    def get_items(self, page_number: int):
        """ Получение нужных элементов для записи в JSON файл.
            page_number (int): номер странцы
            
        """
        logging.info(f"call get_items")
        # Рабта с BS4
        soup = BeautifulSoup(self.data, "lxml")
        item_divs = self.find_article(soup)
        # Перебираем их для обработки
        data_list = []
        for item in item_divs:
            item: BeautifulSoup
            data_list.append(self.create_dic(item,page_number))        
        self.append_data(data_list)
        try:
            # Записываем в файл что мы запарсили эту страницу
            ur.write_url(self.url)
            self.get_source(self.next_page(self.url))
        except Exception as exception:
            logging.exception(f"cant get_source from next_page: {exception}")
        else:
            logging.info(f"Page parsed {page_number}") 
    
    @error_handler
    def page_number(self, url: str) -> int:
        """ Получает номер страницы

        Args:
            url (str): Ссылка для получения номера

        Returns:
            int: Номер страницы ссылки
        """
        spliter = url.split("&")
        page = spliter[3][2:]
        return int(page)
    
    @error_handler
    def next_page(self, url: str) -> str:
        """ Создает новую ссылку

        Args:
            url (str): Принимает старую ссылку

        Returns:
            str: Новая ссылка
        """
        x = url.split("&")
        x[3] = f"p={self.page_number(url)+1}"
        new_url = "&".join(x)
        return new_url
    
    def stop(self):
        """ Выход из программы """
        logging.info(f"call stop") 
        os._exit(1)


if __name__ == "__main__":
    logging.info(f"Parser start") 
    p = Parsing()
    ur = Urls()
    # Создает файл если его нет
    if not os.path.isfile("urls.ini"):
        logging.info(f"clearing urls") 
        ur.clear_urls()
    # Если нет ссылок в ini файле, он начинает с новой, если есть то продолжает
    if len(ur.get_urls) == 0:
        p.get_source(
            "https://kazan.cian.ru/cat.php?deal_type=sale&engine_version=2&offer_type=flat&p=1&region=4777&room1=1")
    else:
        p.get_source(p.next_page(ur.get_urls[len(ur.get_urls)-1]))
