import joblib
import pandas as pd
from sklearn.metrics import classification_report

model_type= joblib.load('ML_Model/planet_type.joblib')
model_temp= joblib.load('ML_Model/planet_temp.joblib')

pl_rade= 0.532
pl_bmasse= 0.1075
pl_eqt= 209.8
pl_insol= 0.431
pl_orbeccen= 0.0935

pl_orbsmax= 1.524
pl_dens = 3.934

st_teff = 5772
st_rade = 1.0

model_params = pd.DataFrame([[
    pl_rade,
    pl_bmasse,
    pl_eqt,
    pl_insol,
    pl_orbeccen
]], columns=[
    "pl_rade",
    "pl_bmasse",
    "pl_eqt",
    "pl_insol",
    "pl_orbeccen"
])
p_type = model_type.predict(model_params)
thermal_type = model_temp.predict(model_params)

planet = {
    "type": p_type[0],
    "thermal_type": thermal_type[0],

    "radius": pl_rade,
    "mass":pl_bmasse,
    "dens":pl_dens,
    "eq_temperature":pl_eqt,
    "insolation":pl_insol,

    "s_temperature": st_teff,
    "s_radius":st_rade,
    "orbital_distance":pl_orbsmax,
    "eccentricity": pl_orbeccen
}

print('p_type: ',p_type,' thermal_type: ',thermal_type)