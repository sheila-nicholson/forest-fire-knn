import pandas as pd
import geopandas as gpd
import numpy as np

#----------------------------------------------------------------------------------------------------------------#
# distance from fire to nearest municipality
#----------------------------------------------------------------------------------------------------------------#
def fire_to_municipality(fires, municipalities):
    
    # must convert to EPSG:3005 ('BC alders') coordinate reference system
    # coordinates and distances will be measured in meters
    fires = fires.to_crs(epsg=3005)
    municipalities = municipalities.to_crs(epsg=3005)

    # find the nearest municipality to each fire
    fire_to_municipality = gpd.sjoin_nearest(left_df=fires, right_df=municipalities[['MUNICIPALITY', 'POPULATION', 'geometry']], how='left', distance_col='municipality_distance_m')

    fire_to_municipality = fire_to_municipality.reset_index()
    fire_to_municipality['municipality_distance_km'] = fire_to_municipality['municipality_distance_m'] / 1000
    fire_to_municipality = fire_to_municipality.rename(columns={'FIRE_NUMBER_x': 'FIRE_NUMBER', })

    print(f'the number of fires in the dataset: {fires.shape[0]:,}')  
    print(f'the number of closest fire - city matches: {fire_to_municipality.shape[0]:,}')
    print(fire_to_municipality[['FIRE_LABEL','FIRE_SIZE_HECTARES', 'IGNITION_DATE', 'MUNICIPALITY','municipality_distance_km']])
    
    dup_mask = fire_to_municipality.duplicated(subset=['FIRE_LABEL'], keep=False)
    # TODO: will still have to deal with the duplicate fires here
    # looking here this occurs when the fire crosses municipality lines therefore I will choose to keep the city with the larger population
    print(f'\n\nmatches with same distance: \n{fire_to_municipality.loc[dup_mask, ['FIRE_LABEL','FIRE_SIZE_HECTARES', 'IGNITION_DATE', 'MUNICIPALITY','POPULATION', 'municipality_distance_km']]}')
    fire_to_municipality = fire_to_municipality.drop(index=[92, 288, 668])
    print(f'the number of closest fire - city matches after dealing with duplicates: {fire_to_municipality.shape[0]:,}')
    
    cols = ['FIRE_LABEL', 'FIRE_NUMBER', 'MUNICIPALITY', 'POPULATION', 'municipality_distance_m', 'municipality_distance_km']
    return fire_to_municipality[cols]


#----------------------------------------------------------------------------------------------------------------#
# distance from fire to nearest BCWS weather station
#----------------------------------------------------------------------------------------------------------------#    
def fire_to_weather_stn(fires, weather_stn):
    
    # ---------------------------------------------------------
    # Match each fire only against stations from the same year
    # ---------------------------------------------------------
    
    # need to convert to a geoPandas dataframe --> must convert longitude-latitude to a shapely.Point object
    # ran into issue here: specify first as the coordinatek system actually used and then convert 
    # if you directly indicated the coordinate system you want to use it does not align correctly 
    geometry_obj = gpd.points_from_xy(weather_stn['LONGITUDE'], weather_stn['LATITUDE'], crs='EPSG:4326')
    weather_stn = gpd.GeoDataFrame(weather_stn, geometry=geometry_obj)

    weather_stn = weather_stn.to_crs(epsg=3005)
    fires = fires.to_crs(epsg=3005)

    match_stns = []

    for fire_year, fires_for_year in fires.groupby('FIRE_YEAR_x'):
        
        # match up the year for weather stations and fires
        stations_for_year = weather_stn.loc[weather_stn['YEAR'].eq(fire_year)]

        # find closest weather stations for each fire
        year_matches = gpd.sjoin_nearest(left_df=fires_for_year, right_df=stations_for_year, how='left', distance_col='weather_station_distance_m',)
        year_matches = year_matches.rename(columns={'LATITUDE_left': 'LATITUDE_fire', 'LONGITUDE_left': 'LONGITUDE_fire', 'LATITUDE_right': 'LATITUDE_weather', 'LONGITUDE_right': 'LONGITUDE_weather', 'FIRE_NUMBER_x': 'FIRE_NUMBER'})

        # append the matches to the list
        match_stns.append(year_matches)

    # concatenate all of the matches back into a single df
    closest_station_matches = pd.concat(match_stns, ignore_index=True)
    closest_station_matches = closest_station_matches.reset_index()
    closest_station_matches['weather_station_distance_km'] = closest_station_matches['weather_station_distance_m'] / 1000

    print('\n\nNumber of fires:', len(fires))
    print('Number of weather station matches:', len(closest_station_matches))
    print(closest_station_matches[['FIRE_LABEL','FIRE_YEAR_x','STATION_CODE','YEAR','weather_station_distance_km']].head())
    
    dup_mask = closest_station_matches.duplicated(subset=['FIRE_LABEL'], keep=False)
    print(f'\n\nmatches with same distance: \n{closest_station_matches.loc[dup_mask, ['FIRE_LABEL', 'STATION_CODE', 'LATITUDE_fire', 'LONGITUDE_fire','LATITUDE_weather', 'LONGITUDE_weather', 'weather_station_distance_km']]}')
    # ultimately, after looking at the duplicates the weather stations are basically the exact same so I will just keep the first match
    closest_station_matches = closest_station_matches.drop(index=[680, 772])
    print(f'Number of weather station matches after dealing with duplicates: {closest_station_matches.shape[0]}')
    
    cols = ['FIRE_LABEL', 'FIRE_NUMBER', 'YEAR', 'STATION_CODE', 'weather_station_distance_m', 'weather_station_distance_km']
    return closest_station_matches[cols]

def main():
    
    # read in datasets
    fires_df = gpd.read_file('intermediate_data/fires_intermediate.geojson')
    municipalities_df = gpd.read_file('intermediate_data/municipalities_intermediate.geojson')
    
    # even though we have municipality data for multiple years, using 2019 data should be sufficient 
    # TODO: check if boundaries change very much year to year or if additional municipalities are added 
    municipalities_df = municipalities_df[municipalities_df['Year'] == 2019]
    weather_df = pd.read_csv('intermediate_data/weather_stations_by_year.csv')

    # find closest municipality and weather station to each fire 
    dist_municipality = fire_to_municipality(fires_df,  municipalities_df)
    dist_weather_stn = fire_to_weather_stn(fires_df, weather_df)
    
    final_df = dist_municipality.merge(right=dist_weather_stn, how='left', on=['FIRE_LABEL', 'FIRE_NUMBER'])
    final_df.to_csv('intermediate_data/fire_distances.csv', index=False)

    
if __name__ == '__main__':
    main()