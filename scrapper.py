import csv
import json
import re

import requests
import time
from datetime import datetime

from retry import retry
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from classes import *
from functools import wraps

# =========================== CONFIGS ===========================
with open("config.json") as json_file:
    config = json.load(json_file)

RIOT_API_KEY = config["API_RIOT_KEY"]
CHROME_DRIVER = config["CHROME_DRIVER"]
# =========================== CONFIGS ===========================


# ========================== CONSTANTS ==========================
OP_GG_COOKIES = (By.CLASS_NAME, "css-47sehv")
LEAGUE_OF_GRAPHS_COOKIES = (By.TAG_NAME, "mat-button")
RETRY_DELAY = 5
MAX_QUERY_IN_WEBDRIVER = 100
# ========================== CONSTANTS ==========================


# ============================ GLOBAL ===========================
def _create_web_driver():
    service = Service(executable_path=CHROME_DRIVER)
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option(
        "prefs",
        {
            "intl.accept_languages": "en,en_US",
            "profile.managed_default_content_settings.images": 2,
        },
    )
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
    chrome_options.add_argument(f"user-agent={user_agent}")
    chrome_options.add_argument("--headless=new")
    # chrome_options.add_experimental_option(
    # "detach",
    # True,
    # )  # Browser stays opened after executing commands
    return webdriver.Chrome(options=chrome_options, service=service)


driver = _create_web_driver()
num_of_query = 0
# ============================ GLOBAL ===========================


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


def decorate_all_functions(function_decorator, exclude: list[str] = None):
    def decorator(cls):
        for name, obj in vars(cls).items():
            if callable(obj) and (
                exclude is None or (exclude is not None and name not in exclude)
            ):
                setattr(cls, name, function_decorator(obj))
        return cls

    return decorator


def refresh_driver(func):
    @wraps(func)
    def wrapper(*args, **kw):
        global num_of_query
        global driver
        num_of_query += 1
        if num_of_query > MAX_QUERY_IN_WEBDRIVER:
            driver.quit()
            driver = _create_web_driver()
            num_of_query = 0
        return func(*args, **kw)

    return wrapper


@decorate_all_functions(
    refresh_driver,
    [
        "__init__",
        "_create_web_driver",
        "accept_op_gg_cookies",
        "accept_log_cookies",
        "get_only_solo_duo_games",
        "get_player_puuid",
        "get_player_mastery_at_champion",
    ],
)
class Scrapper:
    global driver
    num_of_query = 0

    def __init__(self):
        self.op_gg_cookies_accepted = False
        self.log_cookies_accepted = False

    def accept_op_gg_cookies(self):
        if not self.op_gg_cookies_accepted:
            try:
                WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located(OP_GG_COOKIES)
                )

                cookies = driver.find_element(*OP_GG_COOKIES)
                cookies.click()
                self.op_gg_cookies_accepted = True
            except:
                pass

    def accept_log_cookies(self):
        if not self.log_cookies_accepted:
            try:
                WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located(LEAGUE_OF_GRAPHS_COOKIES)
                )

                cookies = driver.find_element(*LEAGUE_OF_GRAPHS_COOKIES)
                cookies.click()
                self.log_cookies_accepted = True
            except:
                pass

    @staticmethod
    def get_only_solo_duo_games():
        # start switching to solo duo tab
        ranked_game_type = driver.find_element(
            By.XPATH, '//button[@value="SOLORANKED"]'
        )
        ranked_game_type.click()

        # make sure that solo duo tab is switched
        start_time = time.time()
        while time.time() - start_time < 15:
            try:
                if_solo_duo_in_games = [
                    "Ranked Solo" in i.text or i.text == "TFT.OP.GG"
                    for i in driver.find_elements(By.CLASS_NAME, "game-type")
                ]
                # print(sum([1 if 'Ranked Solo' in text else 0 for text in list_of_games]), " ", len(list_of_games))
                if False not in if_solo_duo_in_games:
                    break
            except:
                pass

    def get_n_recent_matches(self, n: int, player: Player) -> list[OpggMatch]:
        driver.get(f"https://www.op.gg/summoners/eune/{player.get_opgg_name()}")
        self.accept_op_gg_cookies()
        self.get_only_solo_duo_games()

        # Show more matches if n > 20
        try:
            for _ in range(0, (n - 1) // 20):
                show_more_button = driver.find_element(
                    By.XPATH, '//button[@class="more"]'
                )
                show_more_button.click()
                WebDriverWait(driver, 3).until(
                    EC.text_to_be_present_in_element(
                        (By.XPATH, '//button[@class="more"]'), "Show More"
                    )
                )
        except:
            pass

        # Get matches divs
        matches_div = driver.find_elements(
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

            matches.append(OpggMatch(red_team, blue_team, match_result))

        return matches

    def get_n_players_with_tier(self, n: int, tier: Tier) -> list[Player]:
        def get_n_players_on_page(n: int, page: int) -> list[Player]:
            driver.get(
                f"https://www.op.gg/leaderboards/tier?tier={tier.value}&page={page}"
            )

            players_a = driver.find_elements(By.XPATH, '//a[@class="summoner-link"]')
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

    @staticmethod
    def get_player_puuid(player: Player) -> str:
        api_url = f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{player.name}/{player.tag}?api_key={RIOT_API_KEY}"
        response = requests.get(api_url)
        return response.json()["puuid"]

    def get_player_mastery_at_champion(self, player: Player, champion: Champion) -> int:
        player_puuid = self.get_player_puuid(player)
        api_url = f"https://eun1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{player_puuid}/by-champion/{champion.value}?api_key={RIOT_API_KEY}"
        response = requests.get(api_url)
        return response.json()["championPoints"]

    def get_player_info(self, player: Player) -> PlayerInfo:
        driver.get(
            f"https://www.leagueofgraphs.com/summoner/eune/{player.get_opgg_name()}#championsData-soloqueue"
        )

        # Wait until page are loaded
        WebDriverWait(driver, 2).until(
            lambda wd: driver.execute_script("return document.readyState")
            == "complete",
            "Page taking too long to load",
        )

        rank = driver.find_element(By.CLASS_NAME, "leagueTier").text
        if rank == "Unranked":
            rank = (
                driver.find_element(By.CLASS_NAME, "averageEnnemyLine")
                .find_element(By.CLASS_NAME, "leagueTier")
                .text
            )

        profile_basics = driver.find_element(By.ID, "profileBasicStats")
        charts = profile_basics.find_element(
            By.XPATH, '//div[@data-tab-id="championsData-soloqueue"]'
        ).find_elements(By.CLASS_NAME, "pie-chart")
        total_games_played = int(charts[0].text)
        overall_win_rate = float(charts[1].text.rstrip("%")) / 100

        level = int(
            driver.find_element(By.CLASS_NAME, "bannerSubtitle").text.split(" ")[1]
        )

        # preferred_positions = [
        #     (lane, float(pos.get_attribute("style").strip(chars_to_strip)) / 100)
        #     for lane, pos in zip(Lane, page.find_elements(By.CLASS_NAME, "gauge"))
        # ]  # height: 5.56%;

        return PlayerInfo(
            player,
            overall_win_rate,
            rank,
            total_games_played,
            level,
            -1,
            -1,
            [],
            -1,
        )
        # except Exception as e:
        #     raise Exception(f"Failed to scrap player info for player: {player}")

    @retry(Exception, tries=3, delay=RETRY_DELAY, backoff=0)
    def get_champion_stats(self, champion: Champion, tier: Tier) -> list[ChampStats]:
        counter_picks_class = "css-12a3bv1 ee0p1b91"

        # load page
        driver.get(
            f"https://www.op.gg/champions/{champion_enum_to_name[champion]}/counters/?tier={tier.value}"
        )

        # accept cookies
        self.accept_op_gg_cookies()

        lane_elements = driver.find_elements(
            By.XPATH, '//div[@data-key="FILTER-POSITION"]'
        )

        champion_stats = []

        # can change to go direct from url not click in button
        for lane_elem in lane_elements:
            lane_name = lane_elem.get_attribute("data-value")
            if lane_elem != lane_elements[0]:
                old_lane_flag = new_lane_flag = self.driver.find_element(
                    By.CLASS_NAME, "ee92tbj0"
                ).text.split(".")[0]
                lane_a = lane_elem.find_element(By.TAG_NAME, "a")
                lane_a.click()

                start_time = time.time()
                while time.time() - start_time < 15 and old_lane_flag == new_lane_flag:
                    try:
                        new_lane_flag = self.driver.find_element(
                            By.CLASS_NAME, "ee92tbj0"
                        ).text.split(".")[0]
                    except:
                        pass

            # print(self.drivers.find_element(By.CLASS_NAME, "tier-icon").find_element(By.TAG_NAME, "img").get_attribute("alt"))
            champion_tier = champion_tier_name_to_enum[
                driver.find_element(By.CLASS_NAME, "tier-info").text
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
            counter_picks_trs = driver.find_elements(
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
                ChampStats(
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

    # sometimes the site blocks one player for n sec
    def get_player_stats_on_specific_champion(
        self, player: Player, champion: Champion
    ) -> PlayerStatsOnChamp:
        global driver
        global num_of_query

        driver.get(
            f"https://www.leagueofgraphs.com/summoner/champions/eune/{player.get_opgg_name()}#championsData-soloqueue"
        )

        champion_string = champion_enum_to_name[champion]

        # Wait until page are loaded
        WebDriverWait(driver, 2).until(
            lambda wd: driver.execute_script("return document.readyState")
            == "complete",
            "Page taking too long to load",
        )

        stats_on_all_champions = driver.find_element(
            By.XPATH, "//div[@data-tab-id='championsData-soloqueue']"
        ).find_elements(By.TAG_NAME, "tr")[1:]

        desired_stats = None
        for stat in stats_on_all_champions:
            if (
                champion_string
                in remove_non_alpha_characters(
                    stat.find_element(By.CLASS_NAME, "name").text
                ).lower()
            ):
                desired_stats = stat
                break

        tds = desired_stats.find_elements(By.TAG_NAME, "td")
        total_games_played = int(tds[1].text)
        win_rate = float(tds[2].text[:-1]) / 100

        kda = tds[3].text.split("\n")
        kills = float(kda[0])
        deaths = float(kda[2])
        assists = float(kda[4])

        # idk what now
        if deaths == 0:
            kda_ratio = kills + assists
        else:
            kda_ratio = (kills + assists) / deaths

        average_cs_per_minute = float(tds[4].text)
        average_gold_per_minute = float(tds[5].text)

        mastery_txt = (
            desired_stats.find_element(By.CLASS_NAME, "requireTooltip")
            .get_attribute("tooltip")
            .replace(",", "")
        )
        mastery = int(re.search(r"Points: (\d+)", mastery_txt).group(1))

        result = PlayerStatsOnChamp(
            player,
            champion_string,
            mastery,
            total_games_played,
            win_rate,
            round(kda_ratio, 4),
            average_gold_per_minute,
            average_cs_per_minute,
        )

        return result
        # except Exception as e:
        #     raise Exception(
        #         f"Failed to scrap player {player} stats on champion {champion_string}"
        #     )
