import pandas as pd
import numpy as np
import geopandas as gpd

# note in this entire script 'igd' is ignition date

# kind of features I want to use:
# avg temp 7d before fire
# avg temp day of ignition
# avg humidity 7d before fire
# avg humidity day of ignition
# avg wind speed day of ignition
# avg precipitation 7d before fire
# avg precipitation 30d before fire
# distance to weather station
# distance to municipality
# population of municipality
# season --> one hot encoding

# possible features to add:
# fire region
# elevation
# lat/lon of fire

# YEAR,STATION_CODE,DATE,DAILY_MEAN_TEMPERATURE,DAILY_MEAN_RELATIVE_HUMIDITY,DAILY_MEAN_WIND_SPEED,
# PRECIPITATION,FINE_FUEL_MOISTURE_CODE,INITIAL_SPREAD_INDEX,FIRE_WEATHER_INDEX,DUFF_MOISTURE_CODE,
# DROUGHT_CODE,BUILDUP_INDEX,DANGER_RATING

# I will need: YEAR, STATION_CODE, DATE, DAILY_MEAN_TEMPERATURE, DAILY_MEAN_RELATIVE_HUMIDITY, 
# DAILY_MEAN_WIND_SPEED, PRECIPITATION

# FIRE_LABEL,FIRE_NUMBER,STATION_CODE,weather_station_distance_km

# FIRE_LABEL,FIRE_NUMBER,FIRE_YEAR,FIRE_ID,IGNITION_DATE,




def weather_features(fires, weather, distances):
    
    weather_features_df = pd.DataFrame(distances[['FIRE_LABEL','FIRE_NUMBER','STATION_CODE','weather_station_distance_km']])
    # print(fires.columns)
    weather_features_df = weather_features_df.merge(right=fires[['FIRE_LABEL','FIRE_NUMBER','FIRE_SIZE_HECTARES','IGNITION_DATE']], how='inner', on=['FIRE_LABEL','FIRE_NUMBER'], validate='one_to_one')
    
    weather_features_df['IGNITION_DATE'] = weather_features_df['IGNITION_DATE'].dt.tz_localize(None)
    weather_features_df['IGNITION_DATE'] = weather_features_df['IGNITION_DATE'].dt.normalize()
    weather['IGNITION_DATE'] = weather['IGNITION_DATE'].dt.tz_localize(None)
    weather['IGNITION_DATE'] = weather['IGNITION_DATE'].dt.normalize()
    
    # lets get the rolling averages into the weather df first
    weather = weather.sort_values(['STATION_CODE', 'IGNITION_DATE']).reset_index(drop=True)
    weather = weather.rename(columns= {'DAILY_MEAN_TEMPERATURE': 'avg_tmp_igd',
                                       'DAILY_MEAN_RELATIVE_HUMIDITY': 'avg_hmd_igd',
                                       'DAILY_MEAN_WIND_SPEED': 'avg_wind_igd',
                                       'PRECIPITATION': 'precp_igd'})
    
    # helper function for calculating rolling averages for weather stats
    def previous_days_average(column, days, aggregate_type):
        rolling_result = weather.groupby('STATION_CODE', sort=False) \
                                .rolling(window=days, on='IGNITION_DATE', closed='left', min_periods=1)[column] \
                                .agg(aggregate_type) \
                                .reset_index(drop=True)
        
        return rolling_result.to_numpy()
    
    weather['avg_tmp_7d'] = previous_days_average('avg_tmp_igd', '7D', 'mean')
    weather['avg_hmd_7d'] = previous_days_average('avg_hmd_igd', '7D', 'mean')
    weather['avg_wind_7d'] = previous_days_average('avg_wind_igd', '7D', 'mean')
    weather['total_precp_7d'] = previous_days_average('precp_igd', '7D', 'sum')
    weather['total_precp_30d'] = previous_days_average('precp_igd', '30D', 'sum')
    weather_cols = ['IGNITION_DATE', 'STATION_CODE', 'avg_tmp_igd', 'avg_tmp_7d', 'avg_hmd_igd', 'avg_hmd_7d', 'avg_wind_igd', 'avg_wind_7d', 'precp_igd', 'total_precp_7d', 'total_precp_30d']
    
    
    
    weather_features_df = weather_features_df.merge(right=weather[weather_cols], how='inner', on=['STATION_CODE', 'IGNITION_DATE'])
    
    # print(weather[['avg_tmp_igd', 'avg_tmp_7d', 'avg_hmd_igd', 'avg_hmd_7d', 'avg_wind_igd', 'avg_wind_7d', 'precp_igd', 'total_precp_7d', 'total_precp_30d']])
    # weather[['DATE', 'STATION_CODE', 'avg_tmp_igd', 'avg_tmp_7d', 'avg_hmd_igd', 'avg_hmd_7d', 'avg_wind_igd', 'avg_wind_7d', 'precp_igd', 'total_precp_7d', 'total_precp_30d']].to_csv('test.csv')
    # weather_features_df.to_csv('test.csv', index=False)
    
    return weather_features_df
    
    

def main():
    
    # read in all appropriate datasets:
    fires = gpd.read_file('intermediate_data/fires_intermediate.geojson')
    fires = fires.rename(columns={'FIRE_NUMBER_x': 'FIRE_NUMBER', 'FIRE_YEAR_x': 'FIRE_YEAR'})
    # print(fires[['FIRE_NUMBER', 'FIRE_LABEL']])


    weather = pd.read_csv('intermediate_data/weather_daily.csv')
    weather['DATE'] = weather['DATE'].astype('datetime64[ms, UTC]')
    weather = weather.rename(columns={'DATE': 'IGNITION_DATE'})
    
    distances = pd.read_csv('intermediate_data/fire_distances.csv')
    print(distances[['FIRE_NUMBER', 'FIRE_LABEL']])
    
    # print(distances.dtypes)
    features_df = weather_features(fires, weather, distances)
    distance_cols = ['FIRE_LABEL','FIRE_NUMBER','MUNICIPALITY','POPULATION','municipality_distance_km']
    features_df = features_df.merge(right=distances[distance_cols], how='inner', on=['FIRE_LABEL','FIRE_NUMBER'])
    print(features_df.columns)
    features_df.to_csv('fires_final_dataset.csv', index=False)

    
if __name__ == '__main__':
    main()