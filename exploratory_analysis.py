import import_data
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
import requests
import pandas as pd

'''
what should i consider here?
- look at number of fires per year
- look at average size of fires per year
- average size per year with outliers (violin plot)
- assign severity/size to fires - large, medium, small
- compare # of fires in different fire zones
    will have to import fire zones and determine which zone each fire is in -> jk this is already included

'''

df = import_data.get_data()

# number of fires per year
counts_year = df.groupby("FIRE_YEAR").size()

plt.bar(counts_year.index, counts_year.values)
plt.xlabel("Year")
plt.ylabel("Number of Forest Fires")
plt.title("Number of Forest Fires >1000 hectares per Year")
plt.show()

# hectares burned per year
hectares_year = df.groupby("FIRE_YEAR")["CURRENT_SIZE"].sum()

plt.bar(hectares_year.index, hectares_year.values)
plt.xlabel("Year")
plt.ylabel("Hectares Burned")
plt.title("Hectares Burned by Forest Fires >1000 hectares per Year")
plt.show()
