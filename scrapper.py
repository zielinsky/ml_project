from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dataclasses import make_dataclass
import time, json, requests
import os.path
import re
import csv
from classes import *
import pandas as pd

# =========================== CONFIGS ===========================
with open("config.json") as json_file:
    config = json.load(json_file)

RIOT_API_KEY = config["API_RIOT_KEY"]
CHROME_DRIVER = config["CHROME_DRIVER"]
# =========================== CONFIGS ===========================


# ========================== CONSTANTS ==========================
PLAYERS_CSV_PATH = "data/players.csv"
PLAYERS_INFO_CSV_PATH = "data/playerInfo.csv"
MATCHES_CSV_PATH = "data/matches.csv"
PLAYER_STATS_ON_CHAMP_CSV_PATH = "data/playerStatsOnChamp.csv"
CHAMPION_STATS_CSVS_PATHS = [
    "data/champStats/Top.csv",
    "data/champStats/Jungle.csv",
    "data/champStats/Mid.csv",
    "data/champStats/Adc.csv",
    "data/champStats/Support.csv",
]
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


def replace_all_enum_occurrences(input_str):
    # Using regular expression to find and replace all enum occurrences in the string
    pattern = r"<([A-Za-z0-9_.]+): \d+>"
    # Replace each match with just the enum name
    output_str = re.sub(pattern, r"\1", input_str)
    return output_str


class Scrapper:
    def __init__(self, webdriver_path: str):
        service = Service(executable_path=webdriver_path)
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option(
            "prefs", {"intl.accept_languages": "en,en_US"}
        )
        chrome_options.add_argument("--headless=new")
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
        ranked_game_type = self.driver.find_element(
            By.XPATH, '//button[@value="SOLORANKED"]'
        )
        ranked_game_type.click()
        time.sleep(1.5)
        list_of_games = [
            i.text for i in self.driver.find_elements(By.CLASS_NAME, "game-type")
        ]
        # print(list_of_games.count("Ranked Solo"), " ", len(list_of_games))
        while list_of_games.count("Ranked Solo") != len(list_of_games):
            list_of_games = [
                i.text for i in self.driver.find_elements(By.CLASS_NAME, "game-type")
            ]
            # print(list_of_games.count("Ranked Solo"), " ", len(list_of_games))

    def get_n_recent_matches(self, n: int, player: Player) -> list[Opgg_match]:
        game_info_class_name = "css-j7qwjs e13s2rqz0"

        self.driver.get(f"https://www.op.gg/summoners/eune/{player.get_opgg_name()}")

        # Agree to cookies
        self._accept_op_gg_cookies()

        # Get only solo/duo games
        self.get_only_solo_duo_games()

        # Wait for match history to load on op.gg
        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located(
                (By.XPATH, '//div[@class="' + game_info_class_name + '"]')
            )
        )

        # Show more matches if n > 20
        try:
            for _ in range(0, n // 20):
                show_more_button = self.driver.find_element(
                    By.XPATH, '//button[@class="more"]'
                )
                show_more_button.click()
                time.sleep(3)
        except:
            pass

        time.sleep(4)

        # Get matches divs
        matches_div = self.driver.find_elements(
            By.XPATH, '//div[@class="' + game_info_class_name + '"]'
        )

        matches = []
        for match_div in matches_div[:n]:
            # Open matches details
            button = match_div.find_element(By.CLASS_NAME, "btn-detail")
            button.click()
            time.sleep(1)

            match_info = match_div.find_element(By.TAG_NAME, "th").text
            player_team = "Red" if "Red" in match_info else "Blue"

            match_result = (
                MatchResult.REMAKE
                if "Remake" in match_info
                else MatchResult.BLUE
                if "Victory" in match_info and "Blue" in match_info
                else MatchResult.RED
                if "Victory" in match_info and "Red" in match_info
                else MatchResult.BLUE
                if "Red" in match_info
                else MatchResult.RED
            )

            players_div = match_div.find_elements(By.CLASS_NAME, "overview-player")

            players_info = (
                []
            )  # [(Player(name='DBicek', tag='EUNE'), 'teemo', <Lanes.TOP: 1>), ...]
            for idx, player_div in enumerate(players_div):
                champion_name = (
                    player_div.find_element(By.CLASS_NAME, "champion")
                    .find_element(By.TAG_NAME, "a")
                    .get_attribute("href")
                    .split("/")[4]
                )

                player = (
                    player_div.find_element(By.CLASS_NAME, "name")
                    .find_element(By.TAG_NAME, "a")
                    .get_attribute("href")
                    .split("/")[5]
                )

                player_name = player.split("-")[0]
                player_tag = player.split("-")[1]
                players_info.append(
                    (
                        Player(player_name, player_tag),
                        champion_name_to_enum[champion_name],
                        Lane(idx % 5 + 1),
                    )
                )

            red_team = players_info[0:5] if player_team == "Red" else players_info[5:10]
            blue_team = (
                players_info[5:10] if player_team == "Red" else players_info[0:5]
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
        self._accept_op_gg_cookies()
        self.get_only_solo_duo_games()

        page = self.driver.find_element(By.ID, "__next")

        def find_on_page(name):
            return page.find_element(By.CLASS_NAME, name)

        try:
            find_on_page("win-lose-container")
        except:
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

    def get_champion_stats(self, champion: Champion, tier: Tier) -> list[Champ_stats]:
        counter_picks_class = "css-12a3bv1 ee0p1b91"

        # load page
        self.driver.get(
            f"https://www.op.gg/champions/{champion_enum_to_name[champion]}/counters/?tier={tier.value}"
        )

        # accept cookies
        self._accept_op_gg_cookies()

        lane_elements = self.driver.find_elements(
            By.XPATH, '//div[@data-key="FILTER-POSITION"]'
        )

        champion_stats = []

        # can change to go direct from url not click in button
        for lane_elem in lane_elements:
            lane_name = lane_elem.get_attribute("data-value")
            lane_a = lane_elem.find_element(By.TAG_NAME, "a")
            lane_a.click()
            time.sleep(
                3
            )  # ================================== WTF ========================================

            champion_tier = champion_tier_name_to_enum[
                self.driver.find_element(By.CLASS_NAME, "tier-info").text
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
        self._accept_op_gg_cookies()

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
        self._accept_op_gg_cookies()

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
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="content-container"]/div/table/colgroup')
            )
        )

        # time.sleep(2)
        stats_on_all_champions = [
            elem
            for elem in self.driver.find_elements(
                By.XPATH, '//*[@id="content-container"]/div/table/tbody/*'
            )
        ]

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

    def scrap_player_info_to_csv(self, player: Player):
        header = [
            "date",
            "player",
            "overall_win_rate",
            "rank",
            "total_games_played",
            "level",
            "last_twenty_games_kda_ratio",
            "last_twenty_games_kill_participation",
            "preferred_positions",
            "last_twenty_games_win_rate",
        ]

        csvExists = os.path.exists(PLAYERS_INFO_CSV_PATH)
        date = datetime.today().strftime("%Y/%m/%d %H:%M:%S")
        with open(PLAYERS_INFO_CSV_PATH, "a+", newline="") as file:
            writer = csv.writer(file)

            if not csvExists:
                writer.writerow(header)

            player_stats = self.get_player_info(player)
            writer.writerow(
                [
                    date,
                    player_stats.player,
                    player_stats.overall_win_rate,
                    player_stats.rank,
                    player_stats.total_games_played,
                    player_stats.level,
                    player_stats.last_twenty_games_kda_ratio,
                    player_stats.last_twenty_games_kill_participation,
                    player_stats.preferred_positions,
                    player_stats.last_twenty_games_win_rate,
                ]
            )

    def scrap_n_player_matches_to_csv(self, player: Player, n: int):
        header = [
            "date",
            "match_winner",
            "player_red_1",
            "player_red_2",
            "player_red_3",
            "player_red_4",
            "player_red_5",
            "player_blue_1",
            "player_blue_2",
            "player_blue_3",
            "player_blue_4",
            "player_blue_5",
        ]

        csvExists = os.path.exists(MATCHES_CSV_PATH)
        with open(MATCHES_CSV_PATH, "a+", newline="") as file:
            writer = csv.writer(file)

            if not csvExists:
                writer.writerow(header)
            date = datetime.today().strftime("%Y/%m/%d %H:%M:%S")

            for match in self.get_n_recent_matches(n, player):
                writer.writerow(
                    [
                        date,
                        match.winner,
                        *match.team_red,
                        *match.team_blue,
                    ]
                )

    def scrap_players_to_csv(self, no_of_players: int, tier: Tier):
        header = ["date", "player_name", "player_tag"]

        csvExists = os.path.exists(PLAYERS_CSV_PATH)
        with open(PLAYERS_CSV_PATH, "a+", newline="") as file:
            writer = csv.writer(file)

            if not csvExists:
                writer.writerow(header)
            date = datetime.today().strftime("%Y/%m/%d %H:%M:%S")

            for player in self.get_n_players_with_tier(no_of_players, tier):
                writer.writerow([date, player.name, player.tag])

    def scrap_champ_stats_to_csv(self, tier: Tier):
        champion_column_names = [
            champion_enum_to_name[champion] for champion in Champion
        ]
        header = [
            "champion_name",
            "tier",
            "win_ratio",
            "ban_ratio",
            "pick_ratio",
        ] + champion_column_names

        csvExistsList = [
            os.path.exists(CHAMPION_STATS_CSVS_PATHS[idx]) for idx in range(5)
        ]

        # csvExists = os.path.exists(PLAYERS_CSV_PATH)
        with open(CHAMPION_STATS_CSVS_PATHS[0], "a+", newline="") as top, open(
            CHAMPION_STATS_CSVS_PATHS[1], "a+", newline=""
        ) as jungle, open(CHAMPION_STATS_CSVS_PATHS[2], "a+", newline="") as mid, open(
            CHAMPION_STATS_CSVS_PATHS[3], "a+", newline=""
        ) as adc, open(
            CHAMPION_STATS_CSVS_PATHS[4], "a+", newline=""
        ) as support:
            writers = [csv.writer(file) for file in [top, jungle, mid, adc, support]]

            for idx, writer in enumerate(writers):
                if not csvExistsList[idx]:
                    writer.writerow(header)

            for champion in Champion:
                champ_stats_list = self.get_champion_stats(champion, tier)

                for champ_stats in champ_stats_list:
                    champion_name = champion_enum_to_name[champ_stats.champion]
                    lane = champ_stats.lane
                    champion_tier = champion_tier_enum_to_name[
                        champ_stats.champion_tier
                    ]
                    win_rate = champ_stats.win_rate
                    ban_rate = champ_stats.ban_rate
                    pick_rate = champ_stats.pick_rate
                    match_up_win_rate = champ_stats.match_up_win_rate

                    for champion in Champion:
                        if not champion in match_up_win_rate:
                            match_up_win_rate[champion] = -1.0

                    writers[lane.value - 1].writerow(
                        [
                            champion_name,
                            champion_tier,
                            win_rate,
                            ban_rate,
                            pick_rate,
                            *[
                                match_up_win_rate[champion_name_to_enum[champion_name]]
                                for champion_name in champion_column_names
                            ],
                        ]
                    )

    def scrap_player_stats_on_champ_to_csv(
        self, player: Player, champion: Champion
    ) -> None:
        header = [
            "player",
            "champion",
            "mastery",
            "total_games_played",
            "win_rate",
            "kda_ratio",
            "average_gold_per_minute",
            "average_cs_per_minute",
        ]
        player_stats_on_champ = self.get_player_stats_on_specific_champion(
            player, champion
        )
        csvExists = os.path.exists(PLAYER_STATS_ON_CHAMP_CSV_PATH)
        with open(PLAYER_STATS_ON_CHAMP_CSV_PATH, "a+", newline="") as file:
            writer = csv.writer(file)

            if not csvExists:
                writer.writerow(header)

            writer.writerow(
                [
                    player_stats_on_champ.player,
                    player_stats_on_champ.champion,
                    player_stats_on_champ.mastery,
                    player_stats_on_champ.total_games_played,
                    player_stats_on_champ.win_rate,
                    player_stats_on_champ.kda_ratio,
                    player_stats_on_champ.average_gold_per_minute,
                    player_stats_on_champ.average_cs_per_minute,
                ]
            )

    @staticmethod
    def get_matches_from_csv() -> list[Opgg_match]:
        matches = []
        with open(MATCHES_CSV_PATH, "r", newline="") as file:
            reader = csv.reader(file)

            # skip header
            next(reader, None)

            for row in reader:
                match_result = eval(row[1])
                team_red = [
                    eval(replace_all_enum_occurrences(player)) for player in row[2:7]
                ]
                team_blue = [
                    eval(replace_all_enum_occurrences(player)) for player in row[7:12]
                ]

                matches.append(Opgg_match(team_red, team_blue, match_result))

        return matches

    @staticmethod
    def get_players_from_csv() -> list[Player]:
        players = []
        with open(PLAYERS_CSV_PATH, "r", newline="") as file:
            reader = csv.reader(file)

            # skip header
            next(reader, None)

            for row in reader:
                players.append(Player(row[1], row[2]))

        return players

    @staticmethod
    def get_players_info_from_csv() -> dict[Player, Player_info]:
        with open(PLAYERS_INFO_CSV_PATH, "r", newline="") as file:
            reader = csv.reader(file)

            # skip header
            next(reader, None)
            players_info = {}
            for row in reader:
                player = eval(row[1])
                wr = float(row[2])
                rank = row[3]
                total_games_played = int(row[4])
                level = int(row[5])
                last_twenty_games_kda_ratio = float(row[6])
                last_twenty_games_kill_participation = float(row[7])
                preferred_positions = eval(replace_all_enum_occurrences(row[8]))
                last_twenty_games_win_rate = float(row[9])

                players_info[player] = Player_info(
                    player,
                    wr,
                    rank,
                    total_games_played,
                    level,
                    last_twenty_games_kda_ratio,
                    last_twenty_games_kill_participation,
                    preferred_positions,
                    last_twenty_games_win_rate,
                )

        return players_info

    # Assuming that -1 means that there is no match up
    @staticmethod
    def get_champ_stats_from_csv() -> Dict[Lane, Dict[Champion, Champ_stats]]:
        # Result dict as in function return type
        res = {}
        # Iterate over all lanes
        for lane in Lane:
            # Choose a correct file from list
            file = CHAMPION_STATS_CSVS_PATHS[lane.value - 1]
            # nested dict (Dict[Champion, Champ_stats])
            lane_dict = {}
            with open(file, "r", newline="") as f:
                reader = csv.reader(f)
                header = pd.read_csv(file).columns
                row_length = len(header)

                next(reader, None)

                for row in reader:
                    champion = champion_name_to_enum[row[0]]
                    tier = champion_tier_name_to_enum[row[1]]
                    winrate = float(row[2])
                    banrate = float(row[3])
                    pickrate = float(row[4])
                    matchups = {
                        champion_name_to_enum[header[i]]: float(row[i])
                        for i in range(5, row_length)
                    }
                    lane_dict[champion] = Champ_stats(
                        champion, lane, tier, winrate, banrate, pickrate, matchups
                    )

            res[lane] = lane_dict

        return res

    @staticmethod
    def get_player_stats_on_champ_from_csv() -> (
        Dict[Player, Dict[Champion, Player_stats_on_champ]]
    ):
        with open(PLAYER_STATS_ON_CHAMP_CSV_PATH, "r", newline="") as file:
            reader = csv.reader(file)

            # skip header
            next(reader, None)

            players_stats_on_champ = {}
            for row in reader:
                player = eval(row[0])
                champion = champion_name_to_enum[row[1]]
                mastery = int(row[2])
                total_games_played = int(row[3])
                win_rate = float(row[4])
                kda_ratio = float(row[5])
                average_gold_per_minute = float(row[6])
                average_cs_per_minute = float(row[7])
                player_stats_on_champ = Player_stats_on_champ(
                    player,
                    champion,
                    mastery,
                    total_games_played,
                    win_rate,
                    kda_ratio,
                    average_gold_per_minute,
                    average_cs_per_minute,
                )

                if player in players_stats_on_champ:
                    players_stats_on_champ[player][champion] = player_stats_on_champ
                else:
                    players_stats_on_champ[player] = {champion: player_stats_on_champ}

        return players_stats_on_champ


scrapper = Scrapper(CHROME_DRIVER)

# scrapper.scrap_player_stats_on_champ_to_csv(
#     Player("LilZiele", "EUNE"), Champion.KINDRED
# )
print(scrapper.get_player_stats_on_champ_from_csv())
# scrapper.scrap_champ_stats_to_csv(Tier.PLATINUM)

# print(scrapper.get_champ_stats_from_csv())
# scrapper.scrap_player_info_to_csv(Player("DBicek", "EUNE"))
# print(scrapper.get_players_info_from_csv())
# print(
#     scrapper.get_player_stats_on_specific_champion(
#         Player("DBicek", "EUNE"), Champion.TEEMO
#     )
# )
# scrapper.scrap_players_to_csv(2000, Tier.IRON)
# print(scrapper.get_matches_from_csv())

# print(scrapper.get_players_from_csv())
# for player2 in scrapper.get_n_players_with_tier(2, Tier.PLATINUM):
#     scrapper.scrap_player_info_to_csv(player2)

# scrapper.scrap_all_matches_info_to_csv(4, 15, Tier.ALL)

# scrapper.get_player_info(Player("Roron0a Z0r0", "EUNE")).show()
# print(scrapper.get_n_recent_matches(15, Player("DBicek", "EUNE")))

# print(scrapper.get_champion_stats(Champion.MISS_FORTUNE, Tier.IRON))
# print(scrapper.get_player_mastery_at_champion(Player("DBicek", "EUNE"), Champion.TEEMO))
#
