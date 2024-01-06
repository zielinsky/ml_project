from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from classes import *


class Scrapper:

    def __init__(self, webdriver_path: str):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("detach", True)  # Browser stays opened after executing commands

        service = Service(executable_path=webdriver_path)
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.maximize_window()

    def get_n_recent_matches(self, n: int, player: Player) -> list[Opgg_match]:
        game_info_class_name = "css-j7qwjs e17hr80g0"

        self.driver.get(f"https://www.op.gg/summoners/eune/{player.get_opgg_name()}")

        # Agree to cookies
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "css-47sehv"))
        )

        cookies = self.driver.find_element(By.CLASS_NAME, "css-47sehv")
        cookies.click()

        # Get only solo/duo games
        ranked_game_type = self.driver.find_element(By.XPATH, '//button[@value="SOLORANKED"]')
        ranked_game_type.click()

        # Wait for match history to load on op.gg
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="' + game_info_class_name + '"]'))
        )

        # Open matches details
        button_list = self.driver.find_elements(By.CLASS_NAME, "btn-detail")
        for button in button_list:
            button.click()
            time.sleep(0.01)

        # Get matches elem
        matches_elems = self.driver.find_elements(By.XPATH, '//div[@class="' + game_info_class_name + '"]')

        matches = []
        for match_elem in matches_elems:
            # Victory | Defeat, Red | Blue
            match_result, player_team = tuple(match_elem.find_element(By.TAG_NAME, "th")\
                                                        .text\
                                                        .replace("(", " ")\
                                                        .split(" ")[:2])

            players_elems = match_elem.find_elements(By.CLASS_NAME, "overview-player")

            players_info = []  # [(Player(name='DBicek', tag='EUNE'), 'teemo', <Lanes.TOP: 1>), ...]
            for idx, player_elem in enumerate(players_elems):
                champion = player_elem.find_element(By.CLASS_NAME, "champion") \
                                      .find_element(By.TAG_NAME, "a") \
                                      .get_attribute('href').split("/")[4]

                player = player_elem.find_element(By.CLASS_NAME, "name") \
                                    .find_element(By.TAG_NAME, "a") \
                                    .get_attribute('href').split("/")[5]

                player_name = player.split("-")[0]
                player_tag = player.split("-")[1]
                players_info.append(((Player(player_name, player_tag), champion), Lanes(idx % 5 + 1)))

            red_team = players_info[0:5] if player_team == 'Red' else players_info[5:10]
            blue_team = players_info[5:10] if player_team == 'Red' else players_info[0:5]
            winning_team = player_team if match_result == "Victory" else "Red" if player_team == "Blue" else "Blue"
            winning_team = Teams(1) if winning_team == "Red" else Teams(2)

            matches.append(Opgg_match(red_team, blue_team, winning_team))
        return matches


# scrapper = Scrapper("ml_project/chromedriver")
scrapper = Scrapper("chromedriver.exe")

print(scrapper.get_n_recent_matches(1, Player("DBicek", "EUNE")))
