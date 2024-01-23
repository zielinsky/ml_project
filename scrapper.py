from datetime import datetime

from retry import retry
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, json, requests
from tqdm import tqdm
import csv
import re
from classes import *

# =========================== CONFIGS ===========================
with open("config.json") as json_file:
    config = json.load(json_file)

RIOT_API_KEY = config["API_RIOT_KEY"]
CHROME_DRIVER = config["CHROME_DRIVER"]
# =========================== CONFIGS ===========================


# ========================== CONSTANTS ==========================

RETRY_DELAY = 3
# ========================== CONSTANTS ==========================


def remove_non_alpha_characters(s):
    return re.sub(r"[^a-zA-Z]", "", s)


def remove_duplicates(t):
    return list(dict.fromkeys(t))


def classes_to_csv(list_of_classes, csv_name):
    list_of_classes = [asdict(cls) for cls in list_of_classes]
    keys = list_of_classes[0].keys()
    with open(
        f'data/{csv_name}{datetime.today().strftime("%Y-%m-%d--%H-%M-%S")}.csv',
        "w",
        newline="",
    ) as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(list_of_classes)


class Scrapper:
    def __init__(self, webdriver_path: str):
        service = Service(executable_path=webdriver_path)
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option(
            "prefs", {
                "intl.accept_languages": "en,en_US",
                # block image loading
                "profile.managed_default_content_settings.images": 2
            },

        )
        chrome_options.add_argument("--headless=new")
        # chrome_options.add_experimental_option(
        #    "detach", True
        # )  # Browser stays opened after executing commands

        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        # self.driver.maximize_window()

    def accept_op_gg_cookies(self):
        try:
            WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.CLASS_NAME, "css-47sehv"))
            )

            cookies = self.driver.find_element(By.CLASS_NAME, "css-47sehv")
            cookies.click()
        except:
            pass

    def get_only_solo_duo_games(self):
        # start switching to solo duo tab
        ranked_game_type = self.driver.find_element(
            By.XPATH, '//button[@value="SOLORANKED"]'
        )
        ranked_game_type.click()

        # make sure that solo duo tab is switched
        start_time = time.time()
        while time.time() - start_time < 15:
            try:
                if_solo_duo_in_games = [
                    "Ranked Solo" in i.text or i.text == "TFT.OP.GG"
                    for i in self.driver.find_elements(By.CLASS_NAME, "game-type")
                ]
                # print(sum([1 if 'Ranked Solo' in text else 0 for text in list_of_games]), " ", len(list_of_games))
                if False not in if_solo_duo_in_games:
                    break
            except:
                pass

    @retry((Exception), tries=3, delay=RETRY_DELAY, backoff=0)
    def get_n_recent_matches(self, n: int, player: Player) -> list[Opgg_match]:
        self.driver.get(f"https://www.op.gg/summoners/eune/{player.get_opgg_name()}")
        self.accept_op_gg_cookies()
        self.get_only_solo_duo_games()

        # Show more matches if n > 20
        try:
            for _ in range(0, (n - 1) // 20):
                show_more_button = self.driver.find_element(
                    By.XPATH, '//button[@class="more"]'
                )
                show_more_button.click()
                WebDriverWait(self.driver, 5).until(
                    EC.text_to_be_present_in_element(
                        (By.XPATH, '//button[@class="more"]'), "Show More"
                    )
                )
        except:
            pass
        # Get matches divs
        matches_div = self.driver.find_elements(
            By.CLASS_NAME,
            "e4p6qc61",
        )

        matches = []

        for match_div in matches_div[:n]:
            players_div = match_div.find_elements(
                By.CLASS_NAME,
                "er3mfww1",
            )
            players_match_info = []

            player_team = ""

            for idx, player_div in enumerate(players_div):
                if "is-me" in player_div.get_attribute("class"):
                    player_team = "Red" if idx >= 5 else "Blue"

                champion_name = (
                    player_div.find_element(By.TAG_NAME, "img")
                    .get_attribute("src")
                    .split(".png")[0]
                    .split("/")[-1]
                    .lower()
                )

                player = (
                    player_div.find_element(By.CLASS_NAME, "name")
                    .find_element(By.TAG_NAME, "a")
                    .get_attribute("href")
                    .split("/")[5]
                )

                try:
                    player_name = player.split("-")[0]
                    player_tag = player.split("-")[1]
                except:
                    player_name = player
                    player_tag = "EUNE"

                players_match_info.append(
                    (
                        Player(player_name, player_tag),
                        champion_name_to_enum[champion_name],
                        Lane(idx % 5 + 1),
                    )
                )

            blue_team, red_team = players_match_info[0:5], players_match_info[5:10]

            match_info = match_div.find_element(By.CLASS_NAME, "result").text

            # don't add remakes and blank rows
            if "Remake" in match_info or None in players_match_info:
                continue

            match_result = (
                MatchResult.BLUE
                if "Victory" in match_info and player_team == "Blue"
                else MatchResult.BLUE
                if "Defeat" in match_info and player_team == "Red"
                else MatchResult.RED
                if "Defeat" in match_info and player_team == "Blue"
                else MatchResult.RED
            )

            matches.append(Opgg_match(red_team, blue_team, match_result))

        return matches

    def get_n_players_with_tier(self, n: int, tier: Tier) -> list[Player]:
        def get_n_players_on_page(n: int, page: int) -> list[Player]:
            self.driver.get(
                f"https://www.op.gg/leaderboards/tier?tier={tier.value}&page={page}"
            )

            players_a = self.driver.find_elements(
                By.XPATH, '//a[@class="summoner-link"]'
            )
            players = [
                player_a.get_attribute("href").split("/")[5]
                for player_a in players_a[:n]
            ]

            return [
                Player(player.split("-")[0], player.split("-")[1]) for player in players
            ]

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
        self.accept_op_gg_cookies()

        try:
            self.get_only_solo_duo_games()
        except:
            return self.get_player_info(player)

        page = self.driver.find_element(By.ID, "__next")

        def find_on_page(name):
            return page.find_element(By.CLASS_NAME, name)

        try:
            find_on_page("win-lose-container")
        except:
            # TODO We need to skip matches that have any unranked players
            return Player_info(
                player, None, None, None, None, None, None, None, None
            )  # unranked player

        chars_to_strip = "QWERTYUIOPASDFGHJKLZXCVBNM qwertyuiopasdfghjklzxcvbnm,%:/;"

        overall_win_rate = (
            float(find_on_page("ratio").text.strip(chars_to_strip)) / 100
        )  # Win Rate 17%

        rank = find_on_page("tier").text  # Gold 4

        temp = (
            find_on_page("win-lose").text.replace("W", "").replace("L", "").split(" ")
        )  # 15W 17L
        total_games_played = int(temp[0]) + int(temp[1])

        level = int(find_on_page("level").text)  # 573

        last_twenty_games_kda_ratio = float(
            find_on_page("stats-box").find_element(By.CLASS_NAME, "ratio").text[:-2]
        )  # 2.14:1

        last_twenty_games_kill_participation = (
            float(find_on_page("kill-participantion").text.strip(chars_to_strip)) / 100
        )  # P/Kill 43%

        preferred_positions = [
            (lane, float(pos.get_attribute("style").strip(chars_to_strip)) / 100)
            for lane, pos in zip(Lane, page.find_elements(By.CLASS_NAME, "gauge"))
        ]  # height: 5.56%;

        last_twenty_games_win_rate = (
            float(find_on_page("chart").text.strip(chars_to_strip)) / 100
        )  # 12%

        return Player_info(
            player,
            overall_win_rate,
            rank,
            total_games_played,
            level,
            last_twenty_games_kda_ratio,
            last_twenty_games_kill_participation,
            preferred_positions,
            last_twenty_games_win_rate,
        )

    @retry((Exception), tries=3, delay=RETRY_DELAY, backoff=0)
    def get_champion_stats(self, champion: Champion, tier: Tier) -> list[Champ_stats]:
        counter_picks_class = "css-12a3bv1 ee0p1b91"

        # load page
        self.driver.get(
            f"https://www.op.gg/champions/{champion_enum_to_name[champion]}/counters/?tier={tier.value}"
        )

        # accept cookies
        self.accept_op_gg_cookies()

        lane_elements = self.driver.find_elements(
            By.XPATH, '//div[@data-key="FILTER-POSITION"]'
        )

        champion_stats = []

        # can change to go direct from url not click in button
        for lane_elem in lane_elements:
            lane_name = lane_elem.get_attribute("data-value")
            if lane_elem != lane_elements[0]:
                old_lane_flag = self.driver.find_element(By.CLASS_NAME, "ee92tbj0").text.split('.')[0]
                new_lane_flag = self.driver.find_element(By.CLASS_NAME, "ee92tbj0").text.split('.')[0]
                lane_a = lane_elem.find_element(By.TAG_NAME, "a")
                lane_a.click()

                start_time = time.time()
                while time.time() - start_time < 15 and old_lane_flag == new_lane_flag:
                    try:
                        new_lane_flag = self.driver.find_element(By.CLASS_NAME, "ee92tbj0").text.split('.')[0]
                    except:
                        pass

            champion_tier = champion_tier_name_to_enum[
                self.driver.find_element(By.CLASS_NAME, "tier-icon").find_element(By.TAG_NAME, "img").get_attribute("alt").upper() + " Tier"
            ]

            win_ban_pick_elems = lane_elem.find_elements(
                By.XPATH, '//div[@class="css-1bzqlwn e1psj5i31"]'
            )
            win_rate = float(win_ban_pick_elems[0].text.split("\n")[1].strip("%")) / 100
            pick_rate = (
                float(win_ban_pick_elems[1].text.split("\n")[1].strip("%")) / 100
            )
            ban_rate = float(win_ban_pick_elems[2].text.split("\n")[1].strip("%")) / 100

            # sort by win_rate?
            counter_picks = {}
            counter_picks_trs = self.driver.find_elements(
                By.XPATH, '//tr[@class="' + counter_picks_class + '"]'
            )

            for counter_pick_tr in counter_picks_trs:
                counter_pick_champion = champion_name_to_enum[
                    remove_non_alpha_characters(
                        counter_pick_tr.text.split("\n")[0].lower()
                    )
                ]
                counter_pick_win_ratio = float(
                    counter_pick_tr.text.split("\n")[1].split(" ")[0].strip("%")
                )
                counter_picks[counter_pick_champion] = counter_pick_win_ratio

            champion_stats.append(
                Champ_stats(
                    champion,
                    lane_name_to_enum[lane_name],
                    champion_tier,
                    win_rate,
                    ban_rate,
                    pick_rate,
                    counter_picks,
                )
            )

        return champion_stats

    # Dane ze splita 2 season 2023
    def get_player_stats_on_champions(
        self, player: Player
    ) -> list[Player_stats_on_champ]:
        self.driver.get(
            f"https://www.op.gg/summoners/eune/{player.get_opgg_name()}/champions"
        )
        self.accept_op_gg_cookies()

        # Wait until Season button is clickable
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    '//*[@id="content-container"]/div/div/div[1]/div[2]/div/button',
                )
            )
        )
        season_choice_button = self.driver.find_element(
            By.XPATH, '//*[@id="content-container"]/div/div/div[1]/div[2]/div/button'
        )
        season_choice_button.click()

        # Wait until Season 2023 S2 button is clickable
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    '//*[@id="content-container"]/div/div/div[1]/div[2]/div/div/button[2]',
                )
            )
        )
        season2023_split2_button = self.driver.find_element(
            By.XPATH,
            '//*[@id="content-container"]/div/div/div[1]/div[2]/div/div/button[2]',
        )
        season2023_split2_button.click()

        # Wait until Ranked Solo button is clickable
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="content-container"]/div/div/div[2]/button[2]')
            )
        )
        ranked_solo_games_button = self.driver.find_element(
            By.XPATH, '//*[@id="content-container"]/div/div/div[2]/button[2]'
        )
        ranked_solo_games_button.click()

        # Wait until stats are loaded
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="content-container"]/div/table/colgroup')
            )
        )

        stats_on_champions = [
            elem
            for elem in self.driver.find_elements(
                By.XPATH, '//*[@id="content-container"]/div/table/tbody/*'
            )
        ]

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

            champion = champion_name_to_enum[
                desired_stats_list[1].lower().replace(" ", "").replace("'", "")
            ]
            total_games_played = wins + losses
            win_rate = float(desired_stats_list[4][:-1])
            kda_ratio = float(desired_stats_list[5][:-2])
            average_gold_per_minute = float(desired_stats_list[7].split(" ")[1][1:-1])
            average_cs_per_minute = float(desired_stats_list[7].split(" ")[3][1:-1])
            mastery = self.get_player_mastery_at_champion(player, champion)

            list_of_stats_on_champs.append(
                Player_stats_on_champ(
                    player,
                    champion,
                    mastery,
                    total_games_played,
                    win_rate,
                    kda_ratio,
                    average_gold_per_minute,
                    average_cs_per_minute,
                )
            )

        return list_of_stats_on_champs

    # Data from Season 2023 Split 2
    def get_player_stats_on_specific_champion(
        self, player: Player, champion: Champion
    ) -> Player_stats_on_champ:
        self.driver.get(
            f"https://www.op.gg/summoners/eune/{player.get_opgg_name()}/champions"
        )
        self.accept_op_gg_cookies()

        champion_string = champion_enum_to_name[champion]

        # Wait until Season button is clickable
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    '//*[@id="content-container"]/div/div/div[1]/div[2]/div/button',
                )
            )
        )
        season_choice_button = self.driver.find_element(
            By.XPATH, '//*[@id="content-container"]/div/div/div[1]/div[2]/div/button'
        )
        season_choice_button.click()

        # Wait until Season 2023 S2 button is clickable
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    '//*[@id="content-container"]/div/div/div[1]/div[2]/div/div/button[2]',
                )
            )
        )
        season2023_split2_button = self.driver.find_element(
            By.XPATH,
            '//*[@id="content-container"]/div/div/div[1]/div[2]/div/div/button[2]',
        )
        season2023_split2_button.click()

        # Wait until Ranked Solo button is clickable
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="content-container"]/div/div/div[2]/button[2]')
            )
        )
        ranked_solo_games_button = self.driver.find_element(
            By.XPATH, '//*[@id="content-container"]/div/div/div[2]/button[2]'
        )
        ranked_solo_games_button.click()

        # Wait until stats are loaded
        WebDriverWait(self.driver, 15).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//*[@id="content-container"]/div/table/colgroup')
            )
        )

        # time.sleep(1)
        stats_on_all_champions = self.driver.find_elements(
            By.XPATH, '//*[@id="content-container"]/div/table/tbody/*'
        )

        desired_stats = None
        for stat in stats_on_all_champions:
            if champion_string in stat.text.lower():
                desired_stats = stat
        # TODO Make sure that no empty stats are being saved because the elements take too long to load. The condition
        #  of desired_stats is None is a bandaid so the program doesn't crash for now.

        if (
            "There are no results recorded." in stats_on_all_champions[0].text
            or desired_stats is None
        ):
            return Player_stats_on_champ(player, champion_string, 0, 0, 0, 0, 0, 0)

        desired_stats_list = desired_stats.text.split("\n")

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

        result = Player_stats_on_champ(
            player,
            champion_string,
            mastery,
            total_games_played,
            win_rate,
            kda_ratio,
            average_gold_per_minute,
            average_cs_per_minute,
        )
        return result
