import pandas as pd
import numpy as np

years = [2019, 2020, 2021, 2022, 2023]
year_data = []

station_columns = [
    'STATION_CODE',
    'LATITUDE',
    'LONGITUDE',
    'ELEVATION_M'
]

daily_columns = [
    "PRECIPITATION",
    "FINE_FUEL_MOISTURE_CODE",
    "INITIAL_SPREAD_INDEX",
    "FIRE_WEATHER_INDEX",
    "DUFF_MOISTURE_CODE",
    "DROUGHT_CODE",
    "BUILDUP_INDEX",
    "DANGER_RATING",
]

hourly_columns = [
    "HOURLY_TEMPERATURE",
    "HOURLY_RELATIVE_HUMIDITY",
    "HOURLY_WIND_SPEED",
]



for year in years:
    df_obvs = pd.read_csv(f'raw_data/weather/{year}_BCWS_WX_OBS.csv', dtype={"STATION_NAME": "string", "DATE_TIME": "string"})
    df_stat = pd.read_csv(f'raw_data/weather/{year}_BCWS_WX_STATIONS.csv')


    df_obvs["DATE_TIME"] = pd.to_datetime(df_obvs["DATE_TIME"], format="%Y%m%d%H")

    # create an entry for each day vs each hour of the day
    df_obvs["DATE"] = df_obvs["DATE_TIME"].dt.normalize()

    # Calculate daily averages from hourly readings.
    calc_daily_means = (df_obvs.groupby(["STATION_CODE", "STATION_NAME", "DATE"], as_index=False,)[hourly_columns]
                        .mean()
                        .rename(columns={
                                            "HOURLY_TEMPERATURE": "DAILY_MEAN_TEMPERATURE",
                                            "HOURLY_RELATIVE_HUMIDITY": "DAILY_MEAN_RELATIVE_HUMIDITY",
                                            "HOURLY_WIND_SPEED": "DAILY_MEAN_WIND_SPEED",
                                        }))

    # for the daily values provided at noon
    prov_daily_means = df_obvs.loc[df_obvs["DATE_TIME"].dt.hour == 12, ["STATION_CODE", "STATION_NAME", "DATE", *daily_columns,]].copy()

    # Combine both sets of daily information.
    daily_weather_df = calc_daily_means.merge(prov_daily_means,on=["STATION_CODE", "STATION_NAME", "DATE"], how="left", validate="one_to_one")
    print(daily_weather_df.shape[0])
    daily_weather_df = daily_weather_df.merge(df_stat[station_columns], on='STATION_CODE', how="left",)
    print(daily_weather_df.shape[0])

    daily_weather_df = daily_weather_df.sort_values(by=['DATE', 'STATION_CODE'])
    
    year_data.append(daily_weather_df)
    # daily_weather_df.to_csv('2019_obs_day.csv', index=False)

combined_df = pd.DataFrame()

for year in year_data:
    combined_df = pd.concat([combined_df, year], ignore_index=True)
    

combined_df.to_csv('intermediate_data/weather_intermediate.csv', index=False)
print(combined_df)