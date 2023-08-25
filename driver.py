from selenium.webdriver.chrome.service import Service
from selenium import webdriver
import logging


class Driver:
    def __init__(self):
        service = Service()
        options = webdriver.ChromeOptions()
        self.driver = webdriver.Chrome(service=service,options=options)
        self.driver.maximize_window()
        logging.info("Driver init done")

    @property
    def get_driver(self) -> webdriver:
        return self.driver