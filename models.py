from matplotlib import pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import SelectFromModel
from sklearn.preprocessing import MinMaxScaler
from xgboost import XGBClassifier

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

# col_to_delete = [
#     "blue_team_player_1_wr_on_champ",
#     "blue_team_player_2_wr_on_champ",
#     "blue_team_player_3_wr_on_champ",
#     "blue_team_player_4_wr_on_champ",
#     "blue_team_player_5_wr_on_champ",
#     "blue_team_player_1_gpm_on_champ",
#     "blue_team_player_2_gpm_on_champ",
#     "blue_team_player_3_gpm_on_champ",
#     "blue_team_player_4_gpm_on_champ",
#     "blue_team_player_5_gpm_on_champ",
#     "blue_team_player_1_cspm_on_champ",
#     "blue_team_player_2_cspm_on_champ",
#     "blue_team_player_3_cspm_on_champ",
#     "blue_team_player_4_cspm_on_champ",
#     "blue_team_player_5_cspm_on_champ",
#     "blue_team_player_1_kda_ratio_on_champ",
#     "blue_team_player_2_kda_ratio_on_champ",
#     "blue_team_player_3_kda_ratio_on_champ",
#     "blue_team_player_4_kda_ratio_on_champ",
#     "blue_team_player_5_kda_ratio_on_champ",
#     "blue_team_player_5_average_champion_specific_player_wr",
#     "red_team_player_1_wr_on_champ",
#     "red_team_player_2_wr_on_champ",
#     "red_team_player_3_wr_on_champ",
#     "red_team_player_4_wr_on_champ",
#     "red_team_player_5_wr_on_champ",
#     "red_team_player_1_gpm_on_champ",
#     "red_team_player_2_gpm_on_champ",
#     "red_team_player_3_gpm_on_champ",
#     "red_team_player_4_gpm_on_champ",
#     "red_team_player_5_gpm_on_champ",
#     "red_team_player_1_cspm_on_champ",
#     "red_team_player_2_cspm_on_champ",
#     "red_team_player_3_cspm_on_champ",
#     "red_team_player_4_cspm_on_champ",
#     "red_team_player_5_cspm_on_champ",
#     "red_team_player_1_kda_ratio_on_champ",
#     "red_team_player_2_kda_ratio_on_champ",
#     "red_team_player_3_kda_ratio_on_champ",
#     "red_team_player_4_kda_ratio_on_champ",
#     "red_team_player_5_kda_ratio_on_champ",
#     "red_team_player_5_average_champion_specific_player_wr",
# ]
#
# for col in col_to_delete:
#     X = X.drop(col, axis=1)

# Putting response variable to y
y = df["match_result"]
y = y.apply((lambda row: 0 if row == "RED" else 1))


# Splitting the data into train and test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, train_size=0.7, random_state=42
)
# scaler = MinMaxScaler(feature_range=(0, 1))
# X_train = pd.DataFrame(scaler.fit_transform(X_train))
# X_test = pd.DataFrame(scaler.fit_transform(X_test))


def xgboost_model():
    dtrain = xgb.DMatrix(X_train, label=y_train)
    dtest = xgb.DMatrix(X_test, label=y_test)

    param = {"max_depth": 2, "eta": 1, "objective": "binary:logistic"}
    param["nthread"] = 6
    param["eval_metric"] = "auc"

    evallist = [(dtrain, "train"), (dtest, "eval")]

    num_round = 200
    bst = xgb.train(param, dtrain, num_round, evals=evallist)

    fig, ax = plt.subplots(figsize=(50, 30))
    xgb.plot_importance(bst, ax=ax)
    plt.show()

    # bst = XGBClassifier()
    # bst.fit(X_train, y_train)
    #
    # print(bst.score(X_test, y_test))
    #
    # fig, ax = plt.subplots(figsize=(50, 30))
    # plt.barh(X.columns, bst.feature_importances_)
    #
    # plt.show()


def random_forest():
    classifier_rf = RandomForestClassifier(
        random_state=42, n_jobs=-1, max_depth=25, n_estimators=100, oob_score=True
    )

    classifier_rf.fit(X_train, y_train)

    # checking the oob score
    print(f"OOB score = {classifier_rf.oob_score_}")

    print(classifier_rf.score(X_test, y_test))

    # print(selected_feat)
    fig, ax = plt.subplots(figsize=(50, 30))
    plt.barh(X.columns, classifier_rf.feature_importances_)

    plt.show()


# random_forest()
xgboost_model()
