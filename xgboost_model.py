from csv_handler import DATA_VECTOR_CSV_PATH
import pandas as pd
from sklearn.model_selection import train_test_split
import xgboost as xgb

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
y = y.apply((lambda row: 0 if row == "RED" else 1))

# Splitting the data into train and test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, train_size=0.7, random_state=42
)

dtrain = xgb.DMatrix(X_train, label=y_train)
dtest = xgb.DMatrix(X_test, label=y_test)

param = {"max_depth": 2, "eta": 1, "objective": "binary:logistic"}
param["nthread"] = 6
param["eval_metric"] = "auc"

evallist = [(dtrain, "train"), (dtest, "eval")]

num_round = 10
bst = xgb.train(param, dtrain, num_round, evals=evallist)

ypred = bst.predict(dtest)
