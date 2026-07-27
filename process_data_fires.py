import pandas as pd 
import geopandas as gpd
import numpy as np
import pandas as pd

# print(df_perimeters.columns)
# Index(['geometry', 'FIRE_NUMBER', 'VERSION_NUMBER', 'FIRE_YEAR', 'FIRE_CAUSE',
#        'FIRE_LABEL', 'FIRE_SIZE_HECTARES', 'SOURCE', 'GPS_TRACK_DATE',
#        'LOAD_DATE', 'FIRE_DATE', 'CREATION_METHOD', 'FEATURE_CODE', 'OBJECTID',
#        'FEATURE_AREA_SQM', 'FEATURE_LENGTH_M', 'SHAPE.AREA', 'SHAPE.LEN']
      
# print(df_fire.columns)    
# Index(['geometry', 'LATITUDE', 'LONGITUDE', 'CURRENT_SIZE', 'FIRE_NUMBER',
#        'FIRE_YEAR', 'RESPONSE_TYPE_DESC', 'IGNITION_DATE', 'FIRE_OUT_DATE',
#        'FIRE_CAUSE', 'FIRE_LABEL', 'FIRE_CENTRE', 'ZONE', 'FIRE_ID',
#        'FIRE_TYPE', 'INCIDENT_NAME', 'GEOGRAPHIC_DESCRIPTION', 'FEATURE_CODE',
#        'OBJECTID'],
#       dtype='str')

df_perimeters = gpd.read_file('raw_data/fires/forest_fires_perimeter.geojson')
df_fire = gpd.read_file('raw_data/fires/forest_fires.geojson')

# clean up dataframes and select for certain things

perimeter_cols = [  'geometry',
                    'FIRE_LABEL',
                    'FIRE_SIZE_HECTARES',
                    'FEATURE_AREA_SQM',
                    'FIRE_NUMBER',
                    'FIRE_YEAR']



df_perimeters = df_perimeters[df_perimeters['FIRE_YEAR'] >= 2019]
# df_perimeters = df_perimeters.rename(columns={'geometry': 'perimeter_geometry'})

# keep only the newest version of the entry:
# df_perimeters = df_perimeters.groupby(['FIRE_NUMBER', 'FIRE_YEAR']).agg({'VERSION_NUMBER': 'max'})
df_perimeters = df_perimeters.sort_values(["VERSION_NUMBER", "LOAD_DATE"],na_position="first") \
                             .drop_duplicates(subset=["FIRE_NUMBER", "FIRE_YEAR"], keep="last")
df_perimeters = df_perimeters[perimeter_cols]


df_fire = df_fire[df_fire['FIRE_YEAR'] >= 2019]
# df_fire = df_fire.rename(columns={'geometry': 'point_geometry'})

fire_cols = [   'LATITUDE',
                'LONGITUDE',
                'CURRENT_SIZE',
                'FIRE_YEAR',
                'FIRE_NUMBER',
                'FIRE_LABEL',
                'FIRE_ID',
                'IGNITION_DATE',
                'FIRE_OUT_DATE']

df_fire = df_fire[df_fire['FIRE_TYPE'] == 'Fire']
df_fire['IGNITION_DATE'] = pd.to_datetime(df_fire['IGNITION_DATE'], unit='ms', origin="unix", utc=True, errors="coerce")
df_fire['FIRE_OUT_DATE'] = pd.to_datetime(df_fire['FIRE_OUT_DATE'], unit='ms', origin="unix", utc=True, errors="coerce")
df_fire = df_fire[fire_cols]


print(f'size of perimeter dataset: {df_perimeters.shape[0]:,}')
print(f'size of historical fire dataset: {df_fire.shape[0]:,}')

# final_df = gpd.GeoDataFrame()
# final_df = df_perimeters.merge(df_fire, on=['FIRE_NUMBER', 'FIRE_YEAR'])
final_df = df_perimeters.merge(df_fire, on='FIRE_LABEL')

print(f'size of joined dataset: {final_df.shape[0]:,}')

final_df.to_csv('intermediate_data/fires_intermediate.csv',  index=False)
final_df.to_file('intermediate_data/fires_intermediate.geojson',  driver="GeoJSON")
