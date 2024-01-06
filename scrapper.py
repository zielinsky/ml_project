from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from classes import *
from champions import Champion
import json

with open("config.json") as json_file:
    config = json.load(json_file)

RIOT_API_KEY = config['API_RIOT_KEY']


class Scrapper:

    def __init__(self, webdriver_path: str):
        service = Service(executable_path=webdriver_path)
        chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_argument('--headless=new')
        chrome_options.add_experimental_option("detach", True)  # Browser stays opened after executing commands

        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.maximize_window()

    def get_n_recent_matches(self, n: int, player: Player) -> list[Opgg_match]:
        game_info_class_name = "css-j7qwjs e17hr80g0"

        self.driver.get(f"https://www.op.gg/summoners/eune/{player.get_opgg_name()}")

        # Agree to cookies
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "css-47sehv"))
            )

            cookies = self.driver.find_element(By.CLASS_NAME, "css-47sehv")
            cookies.click()
        except:
            pass

        # Get only solo/duo games
        ranked_game_type = self.driver.find_element(By.XPATH, '//button[@value="SOLORANKED"]')
        ranked_game_type.click()

        # Wait for match history to load on op.gg
        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="' + game_info_class_name + '"]'))
        )

        # Show more matches if n > 20
        try:
            for _ in range(0, n // 20):
                show_more_button = self.driver.find_element(By.XPATH, '//button[@class="more"]')
                show_more_button.click()
                time.sleep(3)
        except:
            pass

        time.sleep(2)
        # Open matches details
        button_list = self.driver.find_elements(By.CLASS_NAME, "btn-detail")[:n]
        for button in button_list:
            button.click()
            time.sleep(0.001)

        # Get matches elem
        matches_div = self.driver.find_elements(By.XPATH, '//div[@class="' + game_info_class_name + '"]')

        matches = []
        for match_div in matches_div[:n]:
            match_info = match_div.find_element(By.TAG_NAME, "th").text
            player_team = "Red" if "Red" in match_info else "Blue"

            match_result = MatchResult.REMAKE if "Remake" in match_info else \
                MatchResult.BLUE if "Victory" in match_info and "Blue" in match_info else \
                    MatchResult.RED if "Victory" in match_info and "Red" in match_info else \
                        MatchResult.BLUE if "Red" in match_info else \
                            MatchResult.RED

            players_div = match_div.find_elements(By.CLASS_NAME, "overview-player")

            players_info = []  # [(Player(name='DBicek', tag='EUNE'), 'teemo', <Lanes.TOP: 1>), ...]
            for idx, player_div in enumerate(players_div):
                champion = player_div.find_element(By.CLASS_NAME, "champion") \
                    .find_element(By.TAG_NAME, "a") \
                    .get_attribute('href').split("/")[4]

                player = player_div.find_element(By.CLASS_NAME, "name") \
                    .find_element(By.TAG_NAME, "a") \
                    .get_attribute('href').split("/")[5]

                player_name = player.split("-")[0]
                player_tag = player.split("-")[1]
                players_info.append(((Player(player_name, player_tag), champion), Lanes(idx % 5 + 1)))

            red_team = players_info[0:5] if player_team == 'Red' else players_info[5:10]
            blue_team = players_info[5:10] if player_team == 'Red' else players_info[0:5]

            matches.append(Opgg_match(red_team, blue_team, match_result))

        return matches

    def get_n_players_with_tier(self, n: int, tier: Tier) -> list[Player]:
        def get_n_players_on_page(n: int, page: int) -> list[Player]:
            self.driver.get(f"https://www.op.gg/leaderboards/{'tier?tier=' + tier.value}&page={page}")

            players_a = self.driver.find_elements(By.XPATH, '//a[@class="summoner-link"]')
            players = [player_a.get_attribute('href').split("/")[5] for player_a in players_a[:n]]

            return [Player(player.split("-")[0], player.split("-")[1]) for player in players]

        players = []
        for i in range(1, (n - 1) // 100 + 2):
            players.extend(get_n_players_on_page(n % 100 if i * 100 > n else 100, i))

        return players

    def get_player_mastery_at_champion(self, player: Player, champion: Champion) -> int:
        pass

    def get_player_info(self, player: Player) -> Player_info:
        pass

    def get_champion_stats(self, champion: Champion) -> Champ_stats:
        pass


# scrapper = Scrapper("ml_project/chromedriver")
scrapper = Scrapper("chromedriver.exe")

for player2 in scrapper.get_n_players_with_tier(100, Tier.PLATINUM):
    time.sleep(5)
    for match in scrapper.get_n_recent_matches(50, player2):
        print(match)
