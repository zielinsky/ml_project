from classes import *
from scrapper import Scrapper
from csv_handler import CsvHandler, DATA_VECTOR_CSV_PATH
from data_conversion import DataVectorConverter
import pandas as pd

from sklearn.feature_selection import SelectFromModel
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import numpy as np

import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(50, 30))

scrapper = Scrapper()
csv_handler = CsvHandler(scrapper)
data_vector_converter = DataVectorConverter(csv_handler)

# Tutaj dajesz ile meczy masz
# data_vector_converter.process_matches(3000)
# /
# data_vector = data_vector_converter.create_data_vector_based_on_matches(600)
#
# data_vector_converter.save_data_vectors_to_csv(data_vector)

df = pd.read_csv(DATA_VECTOR_CSV_PATH)

# shuffle the DataFrame rows
df = df.sample(frac=1)
df = df.drop_duplicates()

# Putting feature variable to X
X = df.drop("match_result", axis=1)

col_to_delete = [
    "blue_team_player_1_wr_on_champ",
    "blue_team_player_2_wr_on_champ",
    "blue_team_player_3_wr_on_champ",
    "blue_team_player_4_wr_on_champ",
    "blue_team_player_5_wr_on_champ",
    "blue_team_player_1_overall_wr",
    "blue_team_player_2_overall_wr",
    "blue_team_player_3_overall_wr",
    "blue_team_player_4_overall_wr",
    "blue_team_player_5_overall_wr",
    "blue_team_player_1_gpm_on_champ",
    "blue_team_player_2_gpm_on_champ",
    "blue_team_player_3_gpm_on_champ",
    "blue_team_player_4_gpm_on_champ",
    "blue_team_player_5_gpm_on_champ",
    "blue_team_player_1_cspm_on_champ",
    "blue_team_player_2_cspm_on_champ",
    "blue_team_player_3_cspm_on_champ",
    "blue_team_player_4_cspm_on_champ",
    "blue_team_player_5_cspm_on_champ",
    "blue_team_player_1_kda_ratio_on_champ",
    "blue_team_player_2_kda_ratio_on_champ",
    "blue_team_player_3_kda_ratio_on_champ",
    "blue_team_player_4_kda_ratio_on_champ",
    "blue_team_player_5_kda_ratio_on_champ",
    # "blue_team_average_player_wr",
    "blue_team_player_5_average_champion_specific_player_wr",
    "red_team_player_1_wr_on_champ",
    "red_team_player_2_wr_on_champ",
    "red_team_player_3_wr_on_champ",
    "red_team_player_4_wr_on_champ",
    "red_team_player_5_wr_on_champ",
    "red_team_player_1_overall_wr",
    "red_team_player_2_overall_wr",
    "red_team_player_3_overall_wr",
    "red_team_player_4_overall_wr",
    "red_team_player_5_overall_wr",
    "red_team_player_1_gpm_on_champ",
    "red_team_player_2_gpm_on_champ",
    "red_team_player_3_gpm_on_champ",
    "red_team_player_4_gpm_on_champ",
    "red_team_player_5_gpm_on_champ",
    "red_team_player_1_cspm_on_champ",
    "red_team_player_2_cspm_on_champ",
    "red_team_player_3_cspm_on_champ",
    "red_team_player_4_cspm_on_champ",
    "red_team_player_5_cspm_on_champ",
    "red_team_player_1_kda_ratio_on_champ",
    "red_team_player_2_kda_ratio_on_champ",
    "red_team_player_3_kda_ratio_on_champ",
    "red_team_player_4_kda_ratio_on_champ",
    "red_team_player_5_kda_ratio_on_champ",
    # "red_team_average_player_wr",
    "red_team_player_5_average_champion_specific_player_wr",
]

for col in col_to_delete:
    X = X.drop(col, axis=1)

# Putting response variable to y
y = df["match_result"]
# now lets split the data into train and test

# Splitting the data into train and test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, train_size=0.5, random_state=42
)


classifier_rf = RandomForestClassifier(
    random_state=42, n_jobs=-1, max_depth=25, n_estimators=100, oob_score=True
)

classifier_rf.fit(X_train, y_train)

# checking the oob score
print(f"OOB score = {classifier_rf.oob_score_}")

print(classifier_rf.score(X_test, y_test))


sel = SelectFromModel(classifier_rf)

selected_feat = X_train.columns[(sel.get_support())]

# print(selected_feat)

plt.barh(X.columns, classifier_rf.feature_importances_)

plt.show()
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
