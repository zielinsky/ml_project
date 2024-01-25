from csv_handler import *
from classes import *
from statistics import mean


class DataVector:
    def __init__(self, csv_handler: CsvHandler) -> None:
        self.csv_handler = csv_handler

    def get_data_necessary_to_process_matches(self):
        # Przydałoby się sprawdzać czy nie robimy jakiś duplikatów graczy oraz tupli (Player, Champion)
        def scrap_data_necessary_to_process_match(match: Opgg_match):
            match_records = match.team_blue + match.team_red
            for player, champion, lane in tqdm(match_records):
                self.csv_handler.scrap_player_info_to_csv(player)
                self.csv_handler.scrap_player_stats_on_champ_to_csv(player, champion)

        matches = self.csv_handler.get_matches_from_csv()
        for match in tqdm(matches):
            scrap_data_necessary_to_process_match(match)

    def create_data_vector_based_on_matches(self):
        matches = self.csv_handler.get_matches_from_csv()
        self.get_data_necessary_to_process_matches()
        players_info = self.csv_handler.get_players_info_from_csv()
        players_stats_on_champ = self.csv_handler.get_players_stats_on_champ_from_csv()
        champions_stats = self.csv_handler.get_champ_stats_from_csv()

        def get_entry_for_player(
            player_info: Player_info, player_stats_on_champion: Player_stats_on_champ
        ) -> DataEntryForPlayer:
            return DataEntryForPlayer(
                player_stats_on_champion.mastery,
                player_stats_on_champion.win_rate,
                player_stats_on_champion.kda_ratio,
                player_stats_on_champion.average_gold_per_minute,
                player_stats_on_champion.average_cs_per_minute,
                player_info.overall_win_rate,
            )

        def get_entry_for_champion(
            champion_stats: Champ_stats,
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
            players_info: dict[Player, Player_info],
            players_stats_on_champion: dict[
                Player, dict[Champion, Player_stats_on_champ]
            ],
            team: list[(Player, Champion, Lane)],
            enemy_team: list[(Player, Champion, Lane)],
        ) -> (list[DataEntryForPlayer], list[ChampionEntry], list[DataEntryTeam]):
            player_entries = []
            champion_entries = []
            for idx, player, champion, lane in enumerate(team):
                player_entries.append(
                    get_entry_for_player(
                        players_info[player],
                        players_stats_on_champion[player][champion],
                    )
                )
                champion_entries.append(
                    get_entry_for_champion(
                        champions_stats[lane][champion],
                        enemy_team[idx][1],
                    )
                )
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
                    [player_entry.player_overall_wr for player_entry in player_entries]
                ),
                mean(
                    [player_entry.player_wr_on_champ for player_entry in player_entries]
                ),
                mean(
                    [champion_entry.match_up_wr for champion_entry in champion_entries]
                ),
            )
            return player_entries, champion_entries, team_entry

        data_vector = []
        for match in matches:
            blue_team = match.team_blue
            red_team = match.team_red
            match_result = match.winner
            match_row = []

            (
                blue_team_players_entries,
                blue_team_champions_entries,
                blue_team_team_entry,
            ) = calculate_vector_entries(
                players_info, players_stats_on_champ, blue_team, red_team
            )
            (
                red_team_players_entries,
                red_team_champions_entries,
                red_team_team_entry,
            ) = calculate_vector_entries(
                players_info, players_stats_on_champ, red_team, blue_team
            )

            match_row.append(
                DataVector(
                    blue_team_players_entries,
                    blue_team_champions_entries,
                    blue_team_team_entry,
                    red_team_players_entries,
                    red_team_champions_entries,
                    red_team_team_entry,
                    match_result,
                )
            )

            data_vector.append(match_row)
