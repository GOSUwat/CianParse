import logging



class UrlWork:
    @property
    def get_urls(self) -> list[str]:
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
        with open("urls.ini", "a", encoding="utf-8") as file:
            file.write(url+"\n")
            file.close()
        logging.info("write_url complete")
        
    def clear_urls(self):
        with open("urls.ini", "w", encoding="utf-8") as file:
            file.write("")
            file.close()


