import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.model_selection import StratifiedKFold, cross_validate
from joblib import dump, load

df = pd.read_csv('../exoplanets_final.csv')

id_cols = [
    "pl_name",
    "hostname",
]

feature_pl = [
    "pl_rade",
    "pl_bmasse",
    "pl_eqt",
    "pl_insol",
    "pl_orbeccen",
]
feature_s = [
    "st_mass",
    "st_rad",
    "st_teff",
    "st_lum",
    "st_met",
]

target_p_type = [
    'P_TYPE'
]
target_temp=[
    'P_TYPE_TEMP'
]
X=df[feature_pl]
y_p_type=df[target_p_type]

X_train_p_type,X_test_p_type,y_train_p_type,y_test_p_type=train_test_split(
    X,
    y_p_type,
    test_size=0.20,
    random_state=42,
    stratify=y_p_type
)

model_p_type = RandomForestClassifier(
    n_estimators=500,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1
)

model_p_type.fit(X_train_p_type, y_train_p_type)

# dump(model_p_type,'planet_type.joblib')

y_pred_p_type = model_p_type.predict(X_test_p_type)
print("Planet Type Classification Report:")
print(classification_report(y_test_p_type, y_pred_p_type))

y_temp=df[target_temp]

X_train_temp,X_test_temp,y_train_temp,y_test_temp=train_test_split(
    X,
    y_temp,
    test_size=0.20,
    random_state=42,
    stratify=y_temp
)

model_temp = RandomForestClassifier(
    n_estimators=500,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1
)

model_temp.fit(X_train_temp, y_train_temp)

y_pred_temp = model_temp.predict(X_test_temp)

print("Temperature Classification Report:")
print(classification_report(y_test_temp, y_pred_temp))
# dump(model_temp,'planet_temp.joblib')
