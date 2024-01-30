import logging

from scrapper import *
from csv_handler import *
from classes import *
from statistics import mean


class DataVectorConverter:
    def __init__(self, csv_handler: CsvHandler) -> None:
        self.csv_handler = csv_handler

    def process_matches(self, num_of_matches: int, index_from: int = 0) -> None:
        matches = self.csv_handler.get_matches_from_csv(num_of_matches)
        matches = matches[index_from:]
        batch_size = 50
        if num_of_matches - index_from < 0:
            return
        for i in tqdm(range(0, num_of_matches - index_from, batch_size)):
            batch_matches = matches[i : i + batch_size]
            self.get_data_necessary_to_process_matches(batch_matches)
            batch_data_vectors = self.create_data_vector_based_on_matches(batch_matches)
            self.save_data_vectors_to_csv(batch_data_vectors)
            time.sleep(10)

    def get_data_necessary_to_process_matches(self, matches: list[OpggMatch]):
        def scrap_data_necessary_to_process_match(match: OpggMatch):
            match_records = match.team_blue + match.team_red
            for player, champion, lane in match_records:
                try:
                    self.csv_handler.scrap_player_info_to_csv(player)
                except:
                    raise Exception(f"Failed to scrap player info for player {player}")
                try:
                    self.csv_handler.scrap_player_stats_on_champ_to_csv(
                        player, champion
                    )
                except:
                    raise Exception(
                        f"Failed to scrap player champion stats for player {player} for champion {champion}"
                    )

        for match in tqdm(matches):
            try:
                scrap_data_necessary_to_process_match(match)
            except Exception as e:
                logging.error(e)
                continue

    def create_data_vector_based_on_matches(
        self, matches: list[OpggMatch]
    ) -> list[DataVector]:
        players_info = self.csv_handler.get_players_info_from_csv()
        players_stats_on_champ = self.csv_handler.get_players_stats_on_champ_from_csv()
        champions_stats = self.csv_handler.get_champ_stats_from_csv()

        def get_entry_for_player(
            player_info: PlayerInfo,
            player_stats_on_champion: PlayerStatsOnChamp,
            is_winner: bool,
        ) -> DataEntryForPlayer:
            # if player_info.total_games_played < 20:
            #     raise KeyError
            won_games = round(
                player_info.total_games_played * player_info.overall_win_rate
            )
            if is_winner:
                won_games = won_games - 1
            new_wr = won_games / (player_info.total_games_played - 1)
            return DataEntryForPlayer(
                player_stats_on_champion.mastery,
                # player_stats_on_champion.win_rate,
                # player_stats_on_champion.kda_ratio,
                # player_stats_on_champion.average_gold_per_minute,
                # player_stats_on_champion.average_cs_per_minute,
                new_wr,
            )

        def get_entry_for_champion(
            champion_stats: ChampStats,
            enemy_champion: Champion,
        ) -> ChampionEntry:
            return ChampionEntry(
                champion_stats.champion_tier.value,
                champion_stats.win_rate,
                champion_stats.ban_rate,
                champion_stats.pick_rate,
                champion_stats.match_up_win_rate[enemy_champion],
            )

        def calculate_vector_entries(
            players_info: dict[Player, PlayerInfo],
            players_stats_on_champion: dict[Player, dict[Champion, PlayerStatsOnChamp]],
            team: list[(Player, Champion, Lane)],
            enemy_team: list[(Player, Champion, Lane)],
            is_winner: bool,
        ) -> (list[DataEntryForPlayer], list[ChampionEntry], list[DataEntryTeam]):
            player_entries = []
            champion_entries = []
            try:
                for idx, (player, champion, lane) in enumerate(team):
                    player_entries.append(
                        get_entry_for_player(
                            players_info[player],
                            players_stats_on_champion[player][champion],
                            is_winner,
                        )
                    )
                    try:
                        champion_entries.append(
                            get_entry_for_champion(
                                champions_stats[lane][champion],
                                enemy_team[idx][1],
                            )
                        )
                    except KeyError:
                        champion_entries.append(ChampionEntry(5, 0.45, 0.0, 0.0, 0.45))

                team_entry = DataEntryTeam(
                    sum(
                        [
                            player_entry.player_mastery_on_champ
                            for player_entry in player_entries
                        ]
                    ),
                    mean(
                        [
                            player_entry.player_mastery_on_champ
                            for player_entry in player_entries
                        ]
                    ),
                    mean(
                        [
                            player_entry.player_overall_wr
                            for player_entry in player_entries
                        ]
                    ),
                    # mean(
                    #     [
                    #         player_entry.player_wr_on_champ
                    #         for player_entry in player_entries
                    #     ]
                    # ),
                    mean(
                        [
                            champion_entry.match_up_wr
                            for champion_entry in champion_entries
                        ]
                    ),
                )
                return player_entries, champion_entries, team_entry
            except KeyError as e:
                logging.error(e)
                raise Exception("Failed to create entry") from e

        data_vector_list = []
        for match in matches:
            blue_team = match.team_blue
            red_team = match.team_red
            match_result = match.winner
            try:
                (
                    blue_team_players_entries,
                    blue_team_champions_entries,
                    blue_team_team_entry,
                ) = calculate_vector_entries(
                    players_info,
                    players_stats_on_champ,
                    blue_team,
                    red_team,
                    match_result == MatchResult.BLUE,
                )
                (
                    red_team_players_entries,
                    red_team_champions_entries,
                    red_team_team_entry,
                ) = calculate_vector_entries(
                    players_info,
                    players_stats_on_champ,
                    red_team,
                    blue_team,
                    match_result == MatchResult.RED,
                )

                data_vector_list.append(
                    DataVector(
                        match_result,
                        blue_team_players_entries,
                        blue_team_champions_entries,
                        blue_team_team_entry,
                        red_team_players_entries,
                        red_team_champions_entries,
                        red_team_team_entry,
                    )
                )
            except Exception as e:
                continue

        return data_vector_list

    @staticmethod
    def save_data_vectors_to_csv(data_vector_list: list[DataVector]) -> None:
        def flatten(xss: list[list[str]]) -> list[str]:
            return [x for xs in xss for x in xs]

        def get_header_entries() -> list[str]:
            def get_entry_header(
                team_name: str, entry_suffixes: list[str], player_num: str = None
            ) -> list[str]:
                if player_num is None:
                    prefix = team_name + "_"
                else:
                    prefix = team_name + "_player_" + player_num + "_"
                entry_header = [prefix + suffix for suffix in entry_suffixes]
                return entry_header

            player_suffixes = [
                "mastery_on_champ",
                # "wr_on_champ",
                # "kda_ratio_on_champ",
                # "gpm_on_champ",
                # "cspm_on_champ",
                "overall_wr",
            ]
            champion_suffixes = [
                "tier",
                "wr",
                "br",
                "pr",
                "match_up_wr",
            ]
            team_suffixes = [
                "total_mastery",
                "average_mastery",
                "average_player_wr",
                # "average_champion_specific_player_wr",
                "average_champion_specific_match_up_wr",
            ]

            header = []
            for team_name in ["blue_team", "red_team"]:
                for player_num in ["1", "2", "3", "4", "5"]:
                    header.append(
                        get_entry_header(team_name, player_suffixes, player_num)
                    )
                for player_num in ["1", "2", "3", "4", "5"]:
                    header.append(
                        get_entry_header(team_name, champion_suffixes, player_num)
                    )
                header.append(get_entry_header(team_name, team_suffixes))
            return flatten(header)

        def append_entry_list_values(
            row: list[any],
            entry: list[DataEntryForPlayer] | list[ChampionEntry],
        ) -> None:
            for x in entry:
                for k, v in asdict(x).items():
                    row.append(v)

        def append_single_entry(row: list[any], entry: DataEntryTeam):
            for k, v in asdict(entry).items():
                row.append(v)

        header = ["match_result"]
        header.extend(get_header_entries())

        csv_exists = os.path.exists(DATA_VECTOR_CSV_PATH)
        with open(DATA_VECTOR_CSV_PATH, "a+", newline="") as file:
            writer = csv.writer(file)

            if not csv_exists:
                writer.writerow(header)
            for data_vector in data_vector_list:
                row = [data_vector.match_result.name]
                append_entry_list_values(row, data_vector.blue_team_players_entries)
                append_entry_list_values(row, data_vector.blue_team_champions_entries)
                append_single_entry(row, data_vector.blue_team_team_entry)
                append_entry_list_values(row, data_vector.red_team_players_entries)
                append_entry_list_values(row, data_vector.red_team_champions_entries)
                append_single_entry(row, data_vector.red_team_team_entry)
                writer.writerow(row)
