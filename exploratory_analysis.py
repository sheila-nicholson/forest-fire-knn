import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv('fires_final_dataset.csv')
df['IGNITION_DATE'] = pd.to_datetime(df['IGNITION_DATE'], errors='coerce',)
df['fire_year'] = df['IGNITION_DATE'].dt.year
df['fire_month'] = df['IGNITION_DATE'].dt.month

# represent the months cyclically rather than 1-12
df['month_sin'] = np.sin(2 * np.pi * df['fire_month'] / 12)
df['month_cos'] = np.cos(2 * np.pi * df['fire_month'] / 12)


# add a bindary encoding for prediction classes
# 1 - fire size is >= 100 hectares
# 0 - fire size is <100 

features = ['avg_tmp_igd', 
            'avg_tmp_7d', 
            'avg_hmd_igd', 
            'avg_hmd_7d', 
            'avg_wind_igd', 
            'avg_wind_7d', 
            'precp_igd', 
            'total_precp_7d', 
            'total_precp_30d', 
            'fire_month',
            'weather_station_distance_km', 
            'municipality_distance_km', 
            'POPULATION',
            'fire_year',
            'month_sin',
            'month_cos',
            'FIRE_SIZE_HECTARES']

X = df[features]
# drop any samples with null features 
X = X.dropna()

fire_class = pd.Series(0, index=X.index, name='fire_size_class')
moderate = X['FIRE_SIZE_HECTARES'] >= 100

fire_class.loc[moderate] = 1

# look at the distribution of fire sizes
plt.hist(np.log10(df['FIRE_SIZE_HECTARES'] + 1), bins=30) # + 1 so there is no log 0
plt.xlabel('log10(Fire Size in Hectares)')
plt.ylabel('Number of Fires')
plt.title('Distribution of Wildfire Sizes')
plt.savefig('plots/dist_wf_size.png')
# plt.show()
plt.close() 


# compare the 7d temperature of small and large(>=100 hectares) fires 
small = df[df['FIRE_SIZE_HECTARES'] < 100]['avg_tmp_7d'].dropna()
large = df[df['FIRE_SIZE_HECTARES'] >= 100 ]['avg_tmp_7d'].dropna()

plt.boxplot([small, large], labels=['< 100 ha', '>= 100 ha'])
plt.xlabel('Fire Size Class')
plt.ylabel('Average Temperature (°C)')
plt.title('7-Day Average Temperature Before Ignition')
plt.savefig('plots/violin_7dtemp.png')
# plt.show()
plt.close() 

# compare the 30d precipiation of small and large(>=100 hectares) fires 
small = df[df['FIRE_SIZE_HECTARES'] < 100]['total_precp_30d'].dropna()
large = df[df['FIRE_SIZE_HECTARES'] >= 100 ]['total_precp_30d'].dropna()

plt.boxplot([small, large], labels=['< 100 ha', '>= 100 ha'])
plt.xlabel('Fire Size Class')
plt.ylabel('Total precipitation in last 30 days (mm)')
plt.title('30-Day Total Precipitation Before Ignition')
plt.savefig('plots/violin_30dprecp.png')
# plt.show()
plt.close() 

# compare the distance to municipality of small and large(>=100 hectares) fires 
small = df[df['FIRE_SIZE_HECTARES'] < 100]['municipality_distance_km'].dropna()
large = df[df['FIRE_SIZE_HECTARES'] >= 100 ]['municipality_distance_km'].dropna()

plt.boxplot([small, large], labels=['< 100 ha', '>= 100 ha'])
plt.xlabel('Fire Size Class')
plt.ylabel('Distance to closest municiplaity (km)')
plt.title('Distance to closest municiplaity')
plt.savefig('plots/violin_dist_munp.png')
# plt.show()
plt.close()

# make a figure to visualize distances
example = df.sample(10, random_state=123)
example = example[['FIRE_LABEL', 'weather_station_distance_km', 'municipality_distance_km']].sort_values('municipality_distance_km')

y = np.arange(len(example))

plt.figure(figsize=(10, 6))

# maximum distance shown on x-axis
max_distance = max(example['weather_station_distance_km'].max(), example['municipality_distance_km'].max())

# grey horizontal line across each fire
plt.hlines(y=y,xmin=0, xmax=max_distance, color='lightgrey', linewidth=1, zorder=0)

# weather station points
plt.scatter(example['weather_station_distance_km'], y, label='Nearest Weather Station')

# municipality points
plt.scatter(example['municipality_distance_km'], y, label='Nearest Municipality')

plt.yticks(y, example['FIRE_LABEL'])

plt.xlabel('Distance (km)')
plt.ylabel('Fire')
plt.title('Distance from Wildfires to Matched Locations')

plt.legend()
plt.tight_layout()
plt.savefig('plots/distances.png')
# plt.show()
plt.close()