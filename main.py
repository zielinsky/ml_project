from classes import *
from scrapper import Scrapper
from csv_handler import CsvHandler, DATA_VECTOR_CSV_PATH
from data_conversion import DataVectorConverter
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

scrapper = Scrapper()
csv_handler = CsvHandler(scrapper)

# csv_handler.scrap_players_and_their_matches_to_csv(20, 40, Tier.GOLD)

# data_vector_converter = DataVectorConverter(csv_handler)
#
# data_vector = data_vector_converter.create_data_vector_based_on_matches(600)
#
# data_vector_converter.save_data_vectors_to_csv(data_vector)

df = pd.read_csv(DATA_VECTOR_CSV_PATH)

# shuffle the DataFrame rows
df = df.sample(frac=1)

# Putting feature variable to X
X = df.drop("match_result", axis=1)
# Putting response variable to y
y = df["match_result"]
# now lets split the data into train and test

# Splitting the data into train and test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, train_size=0.5, random_state=42
)


classifier_rf = RandomForestClassifier(
    random_state=42, n_jobs=-1, max_depth=5, n_estimators=100, oob_score=True
)

classifier_rf.fit(X_train, y_train)

# checking the oob score
print(f"OOB score = {classifier_rf.oob_score_}")

print(classifier_rf.score(X_test, y_test))


# csv_handler.scrap_champ_stats_to_csv(Tier.GOLD)

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
