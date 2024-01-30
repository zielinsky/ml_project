from csv_handler import DATA_VECTOR_CSV_PATH
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier


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

y = df["match_result"]

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
