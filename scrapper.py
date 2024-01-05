from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select
import time


class Scrapper:
    def __init__(self, webdriver_path : str):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("detach", True) #Browser stays opened after executing commands

        service = Service(executable_path=webdriver_path)
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.maximize_window()

    
    