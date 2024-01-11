from datetime import datetime
import os.path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, json, requests
from classes import *
import re
from champions import Champion
import csv

with open("config.json") as json_file:
    config = json.load(json_file)

RIOT_API_KEY = config['API_RIOT_KEY']


def remove_non_alpha_characters(s):
    return re.sub(r'[^a-zA-Z]', '', s)


def classes_to_csv(list_of_classes, csv_name):
    list_of_classes = [asdict(cls) for cls in list_of_classes]
    keys = list_of_classes[0].keys()
    with open(f'data/{csv_name}{datetime.today().strftime("%Y-%m-%d--%H-%M-%S")}.csv', 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(list_of_classes)


class Scrapper:

    def __init__(self, webdriver_path: str):
        service = Service(executable_path=webdriver_path)
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})
        chrome_options.add_argument('--headless=new')
        # chrome_options.add_experimental_option("detach", True)  # Browser stays opened after executing commands

        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        # self.driver.maximize_window()


    def _accept_op_gg_cookies(self):
        try:
            WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.CLASS_NAME, "css-47sehv"))
            )

            cookies = self.driver.find_element(By.CLASS_NAME, "css-47sehv")
            cookies.click()
        except:
            pass

    def get_only_solo_duo_games(self):
        ranked_game_type = self.driver.find_element(By.XPATH, '//button[@value="SOLORANKED"]')
        ranked_game_type.click()
        time.sleep(1.5)
        list_of_games = [i.text for i in self.driver.find_elements(By.CLASS_NAME, 'game-type')]
        #print(list_of_games.count("Ranked Solo"), " ", len(list_of_games))
        while list_of_games.count("Ranked Solo") != len(list_of_games):
            list_of_games = [i.text for i in self.driver.find_elements(By.CLASS_NAME, 'game-type')]
            #print(list_of_games.count("Ranked Solo"), " ", len(list_of_games))

    def get_n_recent_matches(self, n: int, player: Player) -> list[Opgg_match]:
        game_info_class_name = "css-j7qwjs e17hr80g0"

        self.driver.get(f"https://www.op.gg/summoners/eune/{player.get_opgg_name()}")

        # Agree to cookies
        self._accept_op_gg_cookies()

        # Get only solo/duo games
        self.get_only_solo_duo_games()

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

        time.sleep(3)
        # Open matches details
        button_list = self.driver.find_elements(By.CLASS_NAME, "btn-detail")[:n]
        for button in button_list:
            button.click()
            time.sleep(1)

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
                champion_name = player_div.find_element(By.CLASS_NAME, "champion") \
                    .find_element(By.TAG_NAME, "a") \
                    .get_attribute('href').split("/")[4]

                player = player_div.find_element(By.CLASS_NAME, "name") \
                    .find_element(By.TAG_NAME, "a") \
                    .get_attribute('href').split("/")[5]

                player_name = player.split("-")[0]
                player_tag = player.split("-")[1]
                players_info.append(
                    (Player(player_name, player_tag), champion_name_to_enum[champion_name], Lane(idx % 5 + 1)))

            red_team = players_info[0:5] if player_team == 'Red' else players_info[5:10]
            blue_team = players_info[5:10] if player_team == 'Red' else players_info[0:5]

            matches.append(Opgg_match(red_team, blue_team, match_result))

        return matches

    def get_n_players_with_tier(self, n: int, tier: Tier) -> list[Player]:
        def get_n_players_on_page(n: int, page: int) -> list[Player]:
            self.driver.get(f"https://www.op.gg/leaderboards/tier?tier={tier.value}&page={page}")

            players_a = self.driver.find_elements(By.XPATH, '//a[@class="summoner-link"]')
            players = [player_a.get_attribute('href').split("/")[5] for player_a in players_a[:n]]

            return [Player(player.split("-")[0], player.split("-")[1]) for player in players]

        players = []
        for i in range(1, (n - 1) // 100 + 2):
            players.extend(get_n_players_on_page(n % 100 if i * 100 > n else 100, i))

        return players

    def get_player_puuid(self, player: Player) -> str:
        api_url = f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{player.name}/{player.tag}?api_key={RIOT_API_KEY}"
        response = requests.get(api_url)
        return response.json()["puuid"]

    def get_player_mastery_at_champion(self, player: Player, champion: Champion) -> int:
        player_puuid = self.get_player_puuid(player)
        api_url = f"https://eun1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{player_puuid}/by-champion/{champion.value}?api_key={RIOT_API_KEY}"
        response = requests.get(api_url)
        return response.json()["championPoints"]

    def get_player_info(self, player: Player) -> Player_info:
        self.driver.get(f"https://www.op.gg/summoners/eune/{player.get_opgg_name()}")
        # accept cookies
        self._accept_op_gg_cookies()
        self.get_only_solo_duo_games()

        page = self.driver.find_element(By.ID, '__next')
        def find_on_page(name):
            return page.find_element(By.CLASS_NAME, name)

        try:
            find_on_page('win-lose-container')
        except:
            return Player_info(player, None, None, None, None, None, None, None, None) #unranked player

        chars_to_strip = 'QWERTYUIOPASDFGHJKLZXCVBNM qwertyuiopasdfghjklzxcvbnm,%:/;'

        overall_win_rate = float(find_on_page('ratio').text.strip(chars_to_strip)) / 100 #Win Rate 17%

        rank = find_on_page('tier').text #Gold 4

        temp = find_on_page('win-lose').text.replace('W', '').replace('L', '').split(" ") #15W 17L
        total_games_played = int(temp[0]) + int(temp[1])

        level = int(find_on_page('level').text) #573

        last_twenty_games_kda_ratio = float(
            find_on_page('stats-box').find_element(By.CLASS_NAME, 'ratio').text[:-2]) #2.14:1

        last_twenty_games_kill_participation = float(
            find_on_page('kill-participantion').text.strip(chars_to_strip)) / 100 #P/Kill 43%

        preferred_positions = [(lane, float(pos.get_attribute('style').strip(chars_to_strip)) / 100)
                               for lane, pos in zip(Lane, page.find_elements(By.CLASS_NAME, 'gauge'))] #height: 5.56%;

        last_twenty_games_win_rate = float(find_on_page('chart').text.strip(chars_to_strip)) / 100 #12%

        return Player_info(player, overall_win_rate, rank, total_games_played, level, last_twenty_games_kda_ratio,
                           last_twenty_games_kill_participation, preferred_positions, last_twenty_games_win_rate)

    def get_champion_stats(self, champion: Champion, tier: Tier) -> list[Champ_stats]:
        counter_picks_class = "css-12a3bv1 ee0p1b91"

        # load page
        self.driver.get(f"https://www.op.gg/champions/{champion_enum_to_name[champion]}/counters/?tier={tier.value}")

        # accept cookies
        self._accept_op_gg_cookies()

        lane_elements = self.driver.find_elements(By.XPATH, '//div[@data-key="FILTER-POSITION"]')

        champion_stats = []

        # can change to go direct from url not click in button
        for lane_elem in lane_elements:
            lane_name = lane_elem.get_attribute('data-value')
            lane_a = lane_elem.find_element(By.TAG_NAME, "a")
            lane_a.click()
            time.sleep(3)

            champion_tier = champion_tier_name_to_enum[self.driver.find_element(By.CLASS_NAME, "tier-info").text]

            win_ban_pick_elems = lane_elem.find_elements(By.XPATH, '//div[@class="css-1bzqlwn e1psj5i31"]')
            win_rate = float(win_ban_pick_elems[0].text.split("\n")[1].strip('%')) / 100
            pick_rate = float(win_ban_pick_elems[1].text.split("\n")[1].strip('%')) / 100
            ban_rate = float(win_ban_pick_elems[2].text.split("\n")[1].strip('%')) / 100

            # sort by win_rate?
            counter_picks = {}
            counter_picks_trs = self.driver.find_elements(By.XPATH, '//tr[@class="' + counter_picks_class + '"]')
            for counter_pick_tr in counter_picks_trs:
                counter_pick_champion = champion_name_to_enum[
                    remove_non_alpha_characters(counter_pick_tr.text.split("\n")[0].lower())]
                counter_pick_win_ratio = float(counter_pick_tr.text.split("\n")[1].split(" ")[0].strip("%"))
                counter_picks[counter_pick_champion] = counter_pick_win_ratio

            champion_stats.append(
                Champ_stats(champion, lane_name_to_enum[lane_name], champion_tier, win_rate, ban_rate, pick_rate,
                            counter_picks))

        return champion_stats


    # Dane ze splita 2 season 2023
    def get_player_stats_on_champions(self, player : Player) -> list[Player_stats_on_champ]:
        self.driver.get(f"https://www.op.gg/summoners/eune/{player.get_opgg_name()}/champions")
        self._accept_op_gg_cookies()

        # Wait until Season button is clickable        
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="content-container"]/div/div/div[1]/div[2]/div/button'))
        )
        season_choice_button = self.driver.find_element(By.XPATH, '//*[@id="content-container"]/div/div/div[1]/div[2]/div/button')
        season_choice_button.click()

        # Wait until Season 2023 S2 button is clickable
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="content-container"]/div/div/div[1]/div[2]/div/div/button[2]'))
        )
        season2023_split2_button = self.driver.find_element(By.XPATH, '//*[@id="content-container"]/div/div/div[1]/div[2]/div/div/button[2]')
        season2023_split2_button.click()

        # Wait until Ranked Solo button is clickable
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="content-container"]/div/div/div[2]/button[2]'))
        )
        ranked_solo_games_button = self.driver.find_element(By.XPATH, '//*[@id="content-container"]/div/div/div[2]/button[2]')
        ranked_solo_games_button.click()

        # Wait until stats are loaded
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="content-container"]/div/table/colgroup'))
        )

        stats_on_champions = [elem for elem in self.driver.find_elements(By.XPATH, '//*[@id="content-container"]/div/table/tbody/*')]


        list_of_stats_on_champs = []
        for stat in stats_on_champions:
            desired_stats_list = stat.text.split("\n")

            if "W" not in desired_stats_list[2]:
                wins = 0
                desired_stats_list.insert(2, "0W")
            else:
                wins = int(desired_stats_list[2][:-1])
            
            if "L" not in desired_stats_list[3]:
                losses = 0
                desired_stats_list.insert(3, "0L")
            else:
                losses = int(desired_stats_list[3][:-1])
            
            champion = champion_name_to_enum[desired_stats_list[1].lower().replace(" ", "").replace("'", "")]
            total_games_played = wins + losses
            win_rate = float(desired_stats_list[4][:-1])
            kda_ratio = float(desired_stats_list[5][:-2])
            average_gold_per_minute = float(desired_stats_list[7].split(" ")[1][1:-1])
            average_cs_per_minute = float(desired_stats_list[7].split(" ")[3][1:-1])
            mastery = self.get_player_mastery_at_champion(player, champion)

            list_of_stats_on_champs.append(Player_stats_on_champ(player,
                                                                 champion,
                                                                 mastery,
                                                                 total_games_played,
                                                                 win_rate,
                                                                 kda_ratio,
                                                                 average_gold_per_minute,
                                                                 average_cs_per_minute))
            
        return list_of_stats_on_champs

    # Data from Season 2023 Split 2
    def get_player_stats_on_specific_champion(self, player : Player, champion : Champion) -> Player_stats_on_champ:
        self.driver.get(f"https://www.op.gg/summoners/eune/{player.get_opgg_name()}/champions")
        self._accept_op_gg_cookies()

        champion_string = champion_enum_to_name[champion]

        # Wait until Season button is clickable        
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="content-container"]/div/div/div[1]/div[2]/div/button'))
        )
        season_choice_button = self.driver.find_element(By.XPATH, '//*[@id="content-container"]/div/div/div[1]/div[2]/div/button')
        season_choice_button.click()

        # Wait until Season 2023 S2 button is clickable
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="content-container"]/div/div/div[1]/div[2]/div/div/button[2]'))
        )
        season2023_split2_button = self.driver.find_element(By.XPATH, '//*[@id="content-container"]/div/div/div[1]/div[2]/div/div/button[2]')
        season2023_split2_button.click()

        # Wait until Ranked Solo button is clickable
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="content-container"]/div/div/div[2]/button[2]'))
        )
        ranked_solo_games_button = self.driver.find_element(By.XPATH, '//*[@id="content-container"]/div/div/div[2]/button[2]')
        ranked_solo_games_button.click()

        # Wait until stats are loaded
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="content-container"]/div/table/colgroup'))
        )

        # time.sleep(2)
        stats_on_all_champions = [elem for elem in self.driver.find_elements(By.XPATH, '//*[@id="content-container"]/div/table/tbody/*')]

        desired_stats = []
        for stat in stats_on_all_champions:
            if champion_string in stat.text.lower():
                desired_stats = stat

        desired_stats_list = desired_stats.text.split("\n")
        if len(desired_stats_list) == 0:
            return Player_stats_on_champ(player, champion_string, 0, 0, 0, 0, 0, 0)

        """
        Work around of stats where 0 games are won or 0 games are lost on a specific champion.
        In these cases information of 0W or 0L isn't in site's HTML so I insert an artificial 0W/0L info to make it work.
        """
        if "W" not in desired_stats_list[2]:
            wins = 0
            desired_stats_list.insert(2, "0W")
        else:
            wins = int(desired_stats_list[2][:-1])
        
        if "L" not in desired_stats_list[3]:
            losses = 0
            desired_stats_list.insert(3, "0L")
        else:
            losses = int(desired_stats_list[3][:-1])

        total_games_played = wins + losses
        win_rate = float(desired_stats_list[4][:-1])
        kda_ratio = float(desired_stats_list[5][:-2])
        average_gold_per_minute = float(desired_stats_list[7].split(" ")[1][1:-1])
        average_cs_per_minute = float(desired_stats_list[7].split(" ")[3][1:-1])
        mastery = self.get_player_mastery_at_champion(player, champion)

        result = (Player_stats_on_champ(player,
                                        champion_string,
                                        mastery,
                                        total_games_played,
                                        win_rate,
                                        kda_ratio,
                                        average_gold_per_minute,
                                        average_cs_per_minute))
        return result


    def scrap_player_stats_to_csv(self, player: Player):
        header = ['date',
                  'player', 'overall_win_rate', 'rank', 'total_games_played', 'level',
                  'last_twenty_games_kda_ratio',
                  'last_twenty_games_kill_participation', 'preferred_positions', 'last_twenty_games_win_rate']

        csvExists = os.path.exists('data/playersStats.csv')
        date = datetime.today().strftime("%Y/%m/%d %H:%M:%S")
        with open(f'data/playersStats.csv', 'a+', newline='') as file:
            writer = csv.writer(file)

            if not csvExists:
                writer.writerow(header)

            # duplicates can occur -> needs to catch it later
            # if f"Player(name='{player.name}', tag='{player.tag}')" in file.read():
            #     return

            player_stats = self.get_player_info(player)
            writer.writerow([date,
                             player_stats.player, player_stats.overall_win_rate, player_stats.rank,
                             player_stats.total_games_played,
                             player_stats.level, player_stats.last_twenty_games_kda_ratio,
                             player_stats.last_twenty_games_kill_participation,
                             player_stats.preferred_positions, player_stats.last_twenty_games_win_rate])

    def scrap_all_matches_info_to_csv(self, no_of_players: int, no_of_matches: int, tier: Tier):
        header = ['date', 'match_winner',
                  'player_red_1', 'player_red_2', 'player_red_3', 'player_red_4', 'player_red_5',
                  'player_blue_1', 'player_blue_2', 'player_blue_3', 'player_blue_4', 'player_blue_5']

        csvExists = os.path.exists('data/matches.csv')
        with open(f'data/matches.csv', 'a', newline='') as file:
            writer = csv.writer(file)

            if not csvExists:
                writer.writerow(header)
            date = datetime.today().strftime("%Y/%m/%d %H:%M:%S")
            # idea : dict players and at the end scrap_player_stats_to_csv all - no duplicates
            for player in scrapper.get_n_players_with_tier(no_of_players, tier):
                for match in scrapper.get_n_recent_matches(no_of_matches, player):
                    for playerInfo in match.team_red:
                        self.scrap_player_stats_to_csv(playerInfo[0])
                    for playerInfo in match.team_blue:
                        self.scrap_player_stats_to_csv(playerInfo[0])
                    writer.writerow([date,
                           match.winner,
                           *match.team_red,
                           *match.team_blue,
                           ])


# scrapper = Scrapper("ml_project/chromedriver")
scrapper = Scrapper("ml_project/chromedriver")

# for player2 in scrapper.get_n_players_with_tier(100, Tier.PLATINUM):
#     time.sleep(6)
#scrapper.scrap_all_matches_info_to_csv(2, 2, Tier.ALL)

# scrapper.get_player_info(Player("Roron0a Z0r0", "EUNE")).show()
scrapper.get_player_stats_on_champions(Player("DBicek", "EUNE"))

# print(scrapper.get_champion_stats(Champion.MISS_FORTUNE, Tier.IRON))
# print(scrapper.get_player_mastery_at_champion(Player("DBicek", "EUNE"), Champion.TEEMO))
#
