import pandas as pd

url = (
    "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"
    "?query=select%20*%20from%20pscomppars"
    "&format=csv"
)

df = pd.read_csv(url)

print(df.shape)
print(df.head())

df.to_csv("exoplanets.csv", index=False)