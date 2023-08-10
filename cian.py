import os
import json
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

class Driver:
    """Создает и возвращает драйвер"""

    def __init__(self):
        service = Service(ChromeDriverManager(
            version="114.0.5735.90").install())
        self.driver = webdriver.Chrome(service=service)
        self.driver.maximize_window()

    @property
    def get_driver(self):
        """
        Возвращает экземпляр драйвера
        """
        return self.driver


class Urls:
    """ Создает и модифицирует ссылки """
    @property
    def get_urls(self) -> list[str]:
        """
        Превращает текст из файла в список ссылок.
        """
        with open("urls.ini", "r", encoding="utf-8") as file:
            urls = file.read()
            file.close()
            urls = urls.split("\n")
            if "" in urls:
                urls.remove("")
            return urls

    def write_url(self, url):
        """ Добавляет пройденнные ссылки в файл """
        with open("urls.ini", "a", encoding="utf-8") as file:
            file.write(url+"\n")
            file.close()

    def clear_urls(self):
        """ Очищает файл от ссылок """
        with open("urls.ini", "w", encoding="utf-8") as file:
            file.write("")
            file.close()


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
        # Открытие ссылки
        try:
            urls = Urls()
            self.driver.get(url)
            self.url = str(self.driver.current_url)
        except Exception as exception:
            print("Драйвер ", exception)
            self.stop()
        try:
            # Если парсер прошел все страницы
            if self.url in self.url_list:
                urls.clear_urls()
                print("Прошел")
                self.stop()
            else:
                self.url_list = ur.get_urls
                # Создание временного файла с данными
                self.data = self.driver.page_source

        except Exception as exception:
            print("Запись файла ", exception)

        finally:
            # Обработка временного файла с данными
            self.get_items(self.page_number(self.url))

    def get_items(self, page_number: int):
        """ Получение нужных элементов для записи в JSON файл.
            page_number (int): номер странцы
        """
        try:
            # Рабта с BS4
            soup = BeautifulSoup(self.data, "lxml")
            # Ищем все блоки article
            item_divs = soup.find_all("article")
        except Exception as exception:
            print("article ", exception)
        # Перебираем их для обработки
        data_list = []
        for item in item_divs:
            item: BeautifulSoup
            try:
                # Получаем ссылку на предмет
                item_href = item.find(
                    "a", class_="_93444fe79c--media--9P6wN").get("href")
            except Exception as exception:
                print("href ", exception)
            try:
                # Получаем заголовок обьявления
                header = item.find(
                    "span", attrs={"data-mark": "OfferTitle"}).find("span").text
            except Exception as exception:
                print("Header ", exception)
            try:
                # Адрес разделен на несколько блоков, ищем все
                sep_names = item.find_all(
                    "a", class_="_93444fe79c--link--NQlVc")
            except Exception as exception:
                print("sep_names ", exception)
            try:
                # Создаем пустую строку в которую закидваем текст
                addr = ""
                for name in sep_names:
                    addr += f" {name.contents[0]}"
            except Exception as exception:
                print("name_contents ", exception)
            try:
                # Получаем цену предмета
                price = item.find(
                    "span", attrs={"data-mark": "MainPrice"}).find("span").text
            except Exception as exception:
                print("price ", exception)
            try:
                # Получаем описание предмета (не знаю в чем проблема)
                content = item.find(
                    "div", attrs={"data-name": "Description"}).find("p").text
            except Exception as exception:
                print("content ", exception)
            try:
                # Получаем застройщика
                dev = item.find("div",
                                class_="_93444fe79c--name-container--enElO").find("span").text
            except Exception as exception:
                print("dev ", exception)

            try:
                # Создаем словарь для записи в JSON
                new_data = {
                    "Заголовок": header,
                    "Ссылка": item_href,
                    "Адрес": addr,
                    "Цена": price,
                    "Описание": content,
                    "Застройщик": dev,
                    "Номер страницы": page_number
                }
                data_list.append(new_data)
            except Exception as exception:
                print("Dic", exception)
        try:
            with open("file.json", "a", encoding="utf-8") as json_:
                json.dump(data_list, json_, indent=5, ensure_ascii=False)
                json_.close()
        except Exception as exception:
            print("Запись Json", exception)
        try:
            # Записываем в файл что мы запарсили эту страницу
            ur.write_url(self.url)
            # Небольшая задержка (Можно убрать)
            #time.sleep(1)
            self.get_source(self.next_page(self.url))
        except Exception as exception:
            print("next_page g_sourse", exception)

    def page_number(self, url: str):
        """ Получение номера страницы по ссылке """
        spliter = url.split("&")
        page = spliter[3][2:]
        return int(page)

    def next_page(self, url: str) -> str:
        """ Создание следующей ссылки """
        x = url.split("&")
        x[3] = f"p={self.page_number(url)+1}"
        new_url = "&".join(x)
        return new_url

    def stop(self):
        """ Выход из программы """
        os._exit(1)


if __name__ == "__main__":
    p = Parsing()
    ur = Urls()
    # Создает файл если его нет
    if not os.path.isfile("urls.ini"):
        ur.clear_urls()
    # Если нет ссылок в ini файле, он начинает с новой, если есть то продолжает
    if len(ur.get_urls) == 0:
        p.get_source(
            "https://kazan.cian.ru/cat.php?deal_type=sale&engine_version=2&offer_type=flat&p=1&region=4777&room1=1")
    else:
        p.get_source(p.next_page(ur.get_urls[len(ur.get_urls)-1]))
