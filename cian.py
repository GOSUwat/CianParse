from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import os
import json
import time

urs = []
DATA = ""
class Driver:
    def __init__(self):
        service = Service(ChromeDriverManager(version="114.0.5735.90").install())
        self.driver = webdriver.Chrome(service=service)
        self.driver.maximize_window()
    
    @property
    def get_driver(self):
        return self.driver

class Urls:
    @property
    def get_urls(self) -> list:
        #Какие ссылки уже были запарсены
        with open(f"urls.ini","r",encoding="utf-8") as file:
            urls = file.read()
            file.close()
            urls = urls.split("\n")
            if "" in urls:
                urls.remove("")
            return urls
            
    def write_url(self, url):
        #Добавленеи ссылок
        with open(f"urls.ini","a",encoding="utf-8") as file:
            file.write(url+"\n") 
            file.close()
            
    def clear_urls(self):
        with open(f"urls.ini","w",encoding="utf-8") as file:
            file.write("")
            file.close()

class Parsing:
    
    def __init__(self):
        dr = Driver()
        self.driver = dr.get_driver
    
    def get_source(self,url): 
        #Открытие ссылки
        try:
            global urs,DATA
            ur = Urls()
            self.driver.get(url)
            url = str(self.driver.current_url)        
        except Exception as e:
            print("Драйвер ",e)
            self.stop()
            
        try:
            #Если парсер прошел все страницы
            if url in urs:
                ur.clear_urls()
                print("Прошел")
                self.stop()
            else:
                urs = ur.get_urls
                #Создание временного файла с данными
                DATA = self.driver.page_source
                #with open(f"{self.page_number(url)}.html","w",encoding="utf-8") as file:
                #    file.write(self.driver.page_source) 
                #    file.close() 
            
        except Exception as e:
            print("Запись файла ",e)
            
        finally:   
            #Обработка временного файла с данными
            self.get_items(self.page_number(url),url)
            
        
    def get_items(self,page_number,url):
        try:   
            #Открытие временного файла  
            #with open(f"{self.page_number(url)}.html",encoding="utf-8") as file:
            #    src = file.read()
            #    file.close()
            src = DATA
        except Exception as e:
            print("Чтение файла ",e)
            
        try:
            #Рабта с BS4
            soup = BeautifulSoup(src, "lxml")
            #Ищем все блоки article
            item_divs = soup.find_all("article") 
        except Exception as e:
            print("article ",e)
            
        #Перебираем их для обработки
        data_list = []
        for item in item_divs:
            item:BeautifulSoup
            try:
                #Получаем ссылку на предмет
                item_href = item.find("a",class_="_93444fe79c--media--9P6wN").get("href")
            except Exception as e:
                print("href ", e)
                
            try:
                #Получаем заголовок обьявления
                header = item.find("span", attrs={"data-mark":"OfferTitle"}).find("span").text
            except Exception as e:
                print("Header ",e)
                
            try:
                #Адрес разделен на несколько блоков, ищем все
                sep_names = item.find_all("a", class_="_93444fe79c--link--NQlVc")
            except Exception as e:
                print("sep_names ",e) 
                 
            try:             
                #Создаем пустую строку в которую закидваем текст
                adr = ""
                for name in sep_names:
                    adr += f" {name.contents[0]}"
            except Exception as e:
                print("name_contents ",e)
                
            try:
                #Получаем цену предмета
                price = item.find("span",attrs={"data-mark":"MainPrice"}).find("span").text
            except Exception as e:
                print("price ",e)
            
            try:
                #Получаем описание предмета (не знаю в чем проблема)
                content = item.find("div", attrs={"data-name":"Description"}).find("p").text
            except Exception as e:
                print("content ",e)
                
            try:
                #Получаем застройщика
                dev = item.find("div", class_="_93444fe79c--name-container--enElO").find("span").text
            except Exception as e:
                print("dev ",e)


            try:
                #Создаем словарь для записи в JSON
                new_data = {
                    "Заголовок": header,
                    "Ссылка": item_href,
                    "Адрес": adr,
                    "Цена": price,
                    "Описание": content ,
                    "Застройщик": dev,
                    "Номер страницы": page_number, 
                     
                }
                data_list.append(new_data)  
            except Exception as e:
                print("Dic", e)
                
        try:
            with open(f"file.json","a",encoding="utf-8") as js:
                json.dump(data_list,js,indent=5, ensure_ascii= False)       
                js.close() 
        except Exception as e:
            print("Запись Json",e) 
        try:
            #Записываем в файл что мы запарсили эту страницу
            ur.write_url(url)
            #Небольшая задержка (Можно убрать)
            time.sleep(1)
            self.get_source(self.next_page(url))
        except Exception as e:
            print("next_page g_sourse",e)
            
    #получаем номер страницы        
    def page_number(self,url:str):
        x = url.split("&")
        page = x[3][2:]
        return int(page)
    
    #Собираем новую ссылку 
    def next_page(self,url:str):
        x = url.split("&")
        x[3] = f"p={self.page_number(url)+1}"
        new_url = "&".join(x)
        return new_url
      
    def stop(self):
        os._exit(1)
        
        
if __name__ == "__main__":
    p = Parsing()
    ur = Urls()
    #Создает файл если его нет
    if not os.path.isfile("urls.ini"):
        ur.clear_urls()
    #Если нет ссылок в ini файле, он начинает с новой, если есть то продолжает 
    if len(ur.get_urls) == 0:
        p.get_source("https://kazan.cian.ru/cat.php?deal_type=sale&engine_version=2&offer_type=flat&p=1&region=4777&room1=1")
    else:
        p.get_source(p.next_page(ur.get_urls[len(ur.get_urls)-1]))

