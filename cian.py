import os
from parsing import Parsing
from url import UrlWork
import logging

logging.basicConfig(level=logging.INFO, filename="py_log.log",filemode="w",format="%(asctime)s %(levelname)s %(message)s")

if __name__ == "__main__":
    logging.info(f"Parser start") 
    parsing = Parsing()
    url = UrlWork()
    # Создает файл если его нет
    if not os.path.isfile("urls.ini"):
        logging.info(f"clearing urls") 
        url.clear_urls()
    # Если нет ссылок в ini файле, он начинает с новой, если есть то продолжает
    if len(url.get_urls) == 0:
        parsing.get_source(
            "https://kazan.cian.ru/cat.php?deal_type=sale&engine_version=2&offer_type=flat&p=1&region=4777&room1=1")
    else:
        parsing.get_source(parsing.next_page(url.get_urls[len(url.get_urls)-1]))