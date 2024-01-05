from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select
import time
from classes import *


class Scrapper:
    
    def __init__(self, webdriver_path : str):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("detach", True) #Browser stays opened after executing commands

        service = Service(executable_path=webdriver_path)
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.maximize_window()

    
    def get_n_recent_matches(self, n : int, player : Player) -> list[Opgg_match]:
        game_info_class_name = "css-j7qwjs e17hr80g0"

        self.driver.get(f"https://www.op.gg/summoners/eune/{player.get_opgg_name()}")


        # Agree to cookies
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "css-47sehv"))
        )

        cookies = self.driver.find_element(By.CLASS_NAME, "css-47sehv")
        cookies.click()

        ranked_game_type = self.driver.find_element(By.XPATH, '//button[@value="SOLORANKED"]')
        ranked_game_type.click()

        # Wait for match history to load on op.gg
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="' + game_info_class_name + '"]'))
        )
        
        button_list = self.driver.find_elements(By.CLASS_NAME, "btn-detail")
        for button in button_list:
            button.click()
            time.sleep(0.01)

        games = self.driver.find_elements(By.XPATH, '//div[@class="' + game_info_class_name + '"]')

        for game in games:
            champ_name = game.find_elements(By.)


scrapper = Scrapper("ml_project/chromedriver")

scrapper.get_n_recent_matches(1, Player("DBicek", "EUNE"))