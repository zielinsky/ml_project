from matplotlib import pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier

from sklearn.decomposition import PCA
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import MinMaxScaler

from tqdm import tqdm

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
    "blue_team_player_5_average_champion_specific_player_wr",
    "red_team_player_1_wr_on_champ",
    "red_team_player_2_wr_on_champ",
    "red_team_player_3_wr_on_champ",
    "red_team_player_4_wr_on_champ",
    "red_team_player_5_wr_on_champ",
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


def xgboost_model():
    dtrain = xgb.DMatrix(X_train, label=y_train)
    dtest = xgb.DMatrix(X_test, label=y_test)

    param = {"max_depth": 2, "eta": 1, "objective": "binary:logistic"}
    param["nthread"] = 6
    param["eval_metric"] = "auc"

    evallist = [(dtrain, "train"), (dtest, "eval")]

    num_round = 10
    bst = xgb.train(param, dtrain, num_round, evals=evallist)

    # xgb.plot_importance(bst)
    # plt.show()

def random_forest():
    classifier_rf = RandomForestClassifier(
        random_state=42, n_jobs=-1, max_depth=25, n_estimators=100, oob_score=True
    )

    classifier_rf.fit(X_train, y_train)

    # checking the oob score
    print(f"OOB score = {classifier_rf.oob_score_}")

    print(classifier_rf.score(X_test, y_test))

    # sel = SelectFromModel(classifier_rf)
    #
    # selected_feat = X_train.columns[(sel.get_support())]
    #
    # # print(selected_feat)
    #
    # plt.barh(X.columns, classifier_rf.feature_importances_)
    #
    # plt.show()

def find_best_knn_params_and_pca(X_train_knn, X_test_knn):
    best_acc = 0.0
    best_params = {}
    grid_params = {'n_neighbors': range(350, 551)}
    for i in tqdm(range(1, min(X_train_knn.shape[0], X_train_knn.shape[1]) + 1)):
        knn = KNeighborsClassifier(n_jobs=-1)
        grid_search = GridSearchCV(knn, grid_params, cv=5, n_jobs=-1, verbose=0)
        pca = PCA(n_components=i)
        X_train_pca = pca.fit_transform(X_train_knn)
        X_test_pca = pca.fit_transform(X_test_knn)
        grid_search.fit(X_train_pca, y_train)
        model = grid_search.best_estimator_
        test_acc = model.score(X_test_pca, y_test)
        if test_acc > best_acc:
            best_acc = test_acc
            best_params = {'knn': grid_search.best_params_['n_neighbors'], 'pca': i}

    print(f"Best acc: {best_acc}")
    return best_params

def KNN_model(xd):
    # Scale features
    scaler = MinMaxScaler(feature_range=(0, 1))

    x_train_scaled = scaler.fit_transform(X_train)
    X_train_knn = pd.DataFrame(x_train_scaled)

    x_test_scaled = scaler.fit_transform(X_test)
    X_test_knn = pd.DataFrame(x_test_scaled)

    # Get the best PCA model
    # best_params = find_best_knn_params_and_pca(X_train_knn, X_test_knn)
    # print(best_params['knn'], best_params['pca'])
    best_params = {'knn': xd, 'pca': 2}

    pca = PCA(n_components=best_params['pca'])
    # X_train_pca = pca.fit_transform(X_train_knn)
    # X_test_pca = pca.fit_transform(X_test_knn)
    X_train_pca = X_train_knn
    X_test_pca = X_test_knn

    knn = KNeighborsClassifier(n_neighbors=best_params['knn'], n_jobs=-1)
    knn.fit(X_train_pca, y_train)
    # Predict on dataset which model has not seen before
    return knn.score(X_test_pca, y_test)

arr = []
for j in tqdm(range(1000)):
    temp = KNN_model(413)
    #print(temp)
    arr.append(temp)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, train_size=0.7
    )
print(f"Avr acc: {sum(arr) / len(arr)}\nMin: {min(arr)}\nMax:{max(arr)}\nRange: {max(arr) - min(arr)}")
#random_forest()
#xgboost_model()
