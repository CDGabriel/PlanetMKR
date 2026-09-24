import joblib
import pandas as pd

model_type= joblib.load('ML_Model/planet_type.joblib')
model_temp= joblib.load('ML_Model/planet_temp.joblib')

pl_rade= 12.7
pl_bmasse= 1999.1507
pl_eqt= 210.84
pl_insol= 0.3229
pl_orbeccen= 0.71

pl_orbsmax= 2.2
pl_dens = 5.36

st_teff = 5945.0
st_rade = 1.19

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
