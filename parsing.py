from bs4 import BeautifulSoup
import os
import json
import driver
import logging
from url import UrlWork



class Parsing:
    def __init__(self):
        driver_ = driver.Driver()
        self.urls = UrlWork()
        self.driver = driver_.get_driver
        self.url_list = []
        self.data = ""
        self.url = ""
    
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
    def get_source(self, url):
        logging.info(f"get_source url: {url}") 
        # Открытие ссылки
        try:

            self.driver.get(url)
            self.url = str(self.driver.current_url)
        except Exception as exception:
            logging.exception(f"driver get url: {exception}")
            self.stop()
        else:
            logging.info(f"driver get_source done.")
        try:
            if self.url in self.url_list:
                self.urls.clear_urls()
                logging.info(f"parsing done. Closing parser.")
                self.stop()
            else:
                self.url_list = self.urls.get_urls
                self.data = self.driver.page_source
        except Exception as exception:
            logging.exception(f"data exception: {exception}")         
        self.get_items(self.page_number(self.url))
    
    @error_handler
    def find_article(self,soup):
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
        logging.info(f"call get_items")
        soup = BeautifulSoup(self.data, "lxml")
        item_divs = self.find_article(soup)
        data_list = []
        for item in item_divs:
            item: BeautifulSoup
            data_list.append(self.create_dic(item,page_number))        
        self.append_data(data_list)
        try:
            self.urls.write_url(self.url)
            self.get_source(self.next_page(self.url))
        except Exception as exception:
            logging.exception(f"cant get_source from next_page: {exception}")
        else:
            logging.info(f"Page parsed {page_number}") 
    
    @error_handler
    def page_number(self, url: str) -> int:
        spliter = url.split("&")
        page = spliter[3][2:]
        return int(page)
    
    @error_handler
    def next_page(self, url: str) -> str:
        x = url.split("&")
        x[3] = f"p={self.page_number(url)+1}"
        new_url = "&".join(x)
        return new_url
    
    def stop(self):
        logging.info(f"call stop") 
        os._exit(1)