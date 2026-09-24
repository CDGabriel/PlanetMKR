import pandas as pd

df_nasa=pd.read_csv('exoplanets_clean.csv')
df_phl = pd.read_csv('phl.csv')

df = df_nasa.merge(
    df_phl[['P_NAME','P_TYPE','P_TYPE_TEMP']],
    left_on='pl_name',
    right_on='P_NAME',
    how='inner'
    )

df["P_TYPE"] = df["P_TYPE"].replace({
    "Miniterran": "Subterran"
})

df.to_csv('exoplanets_final.csv',index=False)