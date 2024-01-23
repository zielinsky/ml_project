from scrapper import Scrapper
from classes import *
import os.path
import csv
from datetime import datetime
from tqdm import tqdm
import re
import pandas as pd


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


def replace_all_enum_occurrences(input_str):
    # Using regular expression to find and replace all enum occurrences in the string
    pattern = r"<([A-Za-z0-9_.]+): \d+>"
    # Replace each match with just the enum name
    output_str = re.sub(pattern, r"\1", input_str)
    return output_str


class CsvHandler:
    def __init__(self, scrapper: Scrapper):
        self.scrapper = scrapper

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

            player_stats = self.scrapper.get_player_info(player)
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

            for match in self.scrapper.get_n_recent_matches(n, player):
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

            for player in self.scrapper.get_n_players_with_tier(no_of_players, tier):
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

            for champion in tqdm(Champion):
                champ_stats_list = self.scrapper.get_champion_stats(champion, tier)

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
        player_stats_on_champ = self.scrapper.get_player_stats_on_specific_champion(
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

    def scrap_players_and_their_matches_to_csv(
        self, num_of_players: int, num_of_matches: int, tier: Tier
    ):
        self.scrap_players_to_csv(num_of_players, tier)
        players = self.get_players_from_csv()
        for player in tqdm(players):
            self.scrap_n_player_matches_to_csv(player, num_of_matches)

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
    def get_players_stats_on_champ_from_csv() -> (
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
