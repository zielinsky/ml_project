from scrapper import *
from csv_handler import *

scrapper = Scrapper(CHROME_DRIVER)
csv_handler = CsvHandler(scrapper)

csv_handler.scrap_champ_stats_to_csv(Tier.GOLD)

# scrapper.get_champion_stats(Champion.KAYN, Tier.GOLD)
# scrapper.get_n_recent_matches(25, Player("DBicek", "EUNE"))

# csv_handler.scrap_players_and_their_matches_to_csv(200, 50, Tier.PLATINUM)

# scrapper.scrap_data_necessary_to_process_matches()
# scrapper.scrap_player_stats_on_champ_to_csv(
#     Player("LilZiele", "EUNE"), Champion.KINDRED
# )
# print(scrapper.get_player_stats_on_champ_from_csv())
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


# print(scrapper.get_n_recent_matches(15, Player("DBicek", "EUNE")))

# print(scrapper.get_player_mastery_at_champion(Player("DBicek", "EUNE"), Champion.TEEMO))
