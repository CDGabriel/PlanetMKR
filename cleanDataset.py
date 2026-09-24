import pandas as pd
import numpy as np

EARTH_DENSITY = 5.514


df = pd.read_csv('exoplanets_raw.csv')
col_names=list(df.columns)
cols_to_keep=['pl_name','hostname','pl_rade','pl_bmasse','pl_dens','pl_eqt','pl_insol','pl_orbper','pl_orbsmax','pl_orbeccen','st_mass','st_rad','st_teff','st_lum','st_met']

#Keep needed cols
for col_name in col_names:
    if col_name not in cols_to_keep:
        df.drop(col_name,axis=1,inplace=True)

median_cols=['pl_rade','pl_bmasse','pl_dens','pl_eqt','pl_insol','pl_orbper','pl_orbsmax','pl_orbeccen','st_mass','st_rad','st_teff','st_lum','st_met']

#Drop NaN
df = df.dropna(subset=['pl_bmasse','pl_rade','pl_orbeccen'])

# pl_dens Calc
df['pl_dens'] = df['pl_dens'].fillna((df['pl_bmasse']/df['pl_rade']**3)*EARTH_DENSITY)

df=df.dropna()
df.to_csv("exoplanets_clean.csv", index=False)