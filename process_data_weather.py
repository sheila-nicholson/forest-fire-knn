from pathlib import Path

import pandas as pd


years = [2019, 2020, 2021, 2022, 2023]

station_columns = [
    "STATION_CODE",
    "LATITUDE",
    "LONGITUDE",
    "ELEVATION_M",
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

station_year_frames = []
daily_weather_frames = []

output_directory = Path("intermediate_data")
output_directory.mkdir(parents=True, exist_ok=True)


for year in years:
    observations_path = Path(
        f"raw_data/weather/{year}_BCWS_WX_OBS.csv"
    )
    stations_path = Path(
        f"raw_data/weather/{year}_BCWS_WX_STATIONS.csv"
    )

    # Read station codes as strings in both tables so that the join keys
    # always have the same data type.
    df_obvs = pd.read_csv(
        observations_path,
        dtype={
            "STATION_CODE": "string",
            "STATION_NAME": "string",
            "DATE_TIME": "string",
        },
    )

    df_stat = pd.read_csv(
        stations_path,
        dtype={
            "STATION_CODE": "string",
        },
    )

    # --------------------------------------------------------------
    # 1. Create station metadata for this year
    # --------------------------------------------------------------

    station_year_df = df_stat[station_columns].copy()
    station_year_df.insert(0, "YEAR", year)

    # Remove rows that are completely identical.
    station_year_df = station_year_df.drop_duplicates()

    # There should be only one metadata record for each station/year.
    duplicate_station_keys = station_year_df.duplicated(
        subset=["YEAR", "STATION_CODE"],
        keep=False,
    )

    if duplicate_station_keys.any():
        duplicate_rows = station_year_df.loc[
            duplicate_station_keys
        ].sort_values(["YEAR", "STATION_CODE"])

        raise ValueError(
            f"Conflicting station metadata found for {year}:\n"
            f"{duplicate_rows}"
        )

    station_year_frames.append(station_year_df)

    # --------------------------------------------------------------
    # 2. Create daily weather data for this year
    # --------------------------------------------------------------

    df_obvs["DATE_TIME"] = pd.to_datetime(
        df_obvs["DATE_TIME"],
        format="%Y%m%d%H",
        errors="raise",
    )

    df_obvs["DATE"] = df_obvs["DATE_TIME"].dt.normalize()

    # Check that the file contains only records from the expected year.
    unexpected_years = df_obvs.loc[
        df_obvs["DATE"].dt.year.ne(year),
        ["STATION_CODE", "DATE_TIME"],
    ]

    if not unexpected_years.empty:
        raise ValueError(
            f"The {year} observation file contains dates outside {year}:\n"
            f"{unexpected_years.head()}"
        )

    # Calculate daily averages from the hourly measurements.
    calculated_daily_means = (
        df_obvs
        .groupby(
            ["STATION_CODE", "DATE"],
            as_index=False,
        )[hourly_columns]
        .mean()
        .rename(
            columns={
                "HOURLY_TEMPERATURE":
                    "DAILY_MEAN_TEMPERATURE",
                "HOURLY_RELATIVE_HUMIDITY":
                    "DAILY_MEAN_RELATIVE_HUMIDITY",
                "HOURLY_WIND_SPEED":
                    "DAILY_MEAN_WIND_SPEED",
            }
        )
    )

    # The provided daily weather indices are recorded in the noon row.
    provided_daily_values = df_obvs.loc[
        df_obvs["DATE_TIME"].dt.hour.eq(12),
        [
            "STATION_CODE",
            "DATE",
            *daily_columns,
        ],
    ].copy()

    # Check that there is no more than one noon row per station/day.
    duplicate_noon_rows = provided_daily_values.duplicated(
        subset=["STATION_CODE", "DATE"],
        keep=False,
    )

    if duplicate_noon_rows.any():
        duplicate_rows = provided_daily_values.loc[
            duplicate_noon_rows
        ].sort_values(["STATION_CODE", "DATE"])

        raise ValueError(
            f"Multiple noon records found for {year}:\n"
            f"{duplicate_rows}"
        )

    daily_weather_df = calculated_daily_means.merge(
        provided_daily_values,
        on=["STATION_CODE", "DATE"],
        how="left",
        validate="one_to_one",
    )

    daily_weather_df.insert(0, "YEAR", year)

    # Verify that every weather station exists in the station metadata.
    daily_weather_df = daily_weather_df.merge(
        station_year_df[["YEAR", "STATION_CODE"]],
        on=["YEAR", "STATION_CODE"],
        how="left",
        validate="many_to_one",
        indicator=True,
    )

    missing_stations = daily_weather_df.loc[
        daily_weather_df["_merge"].eq("left_only"),
        ["YEAR", "STATION_CODE"],
    ].drop_duplicates()

    if not missing_stations.empty:
        raise ValueError(
            "Weather observations were found for stations missing from "
            f"the station metadata:\n{missing_stations}"
        )

    daily_weather_df = (
        daily_weather_df
        .drop(columns="_merge")
        .sort_values(["DATE", "STATION_CODE"])
        .reset_index(drop=True)
    )

    daily_weather_frames.append(daily_weather_df)


# ------------------------------------------------------------------
# Combine all years
# ------------------------------------------------------------------

stations_by_year = (
    pd.concat(station_year_frames, ignore_index=True)
    .sort_values(["YEAR", "STATION_CODE"])
    .reset_index(drop=True)
)

daily_weather = (
    pd.concat(daily_weather_frames, ignore_index=True)
    .sort_values(["DATE", "STATION_CODE"])
    .reset_index(drop=True)
)


# ------------------------------------------------------------------
# Save the two linked tables
# ------------------------------------------------------------------

stations_by_year.to_csv(
    output_directory / "weather_stations_by_year.csv",
    index=False,
)

daily_weather.to_csv(
    output_directory / "weather_daily.csv",
    index=False,
)


print("Station table:")
print(stations_by_year)
print(stations_by_year.shape)

print("\nDaily weather table:")
print(daily_weather)
print(daily_weather.shape)