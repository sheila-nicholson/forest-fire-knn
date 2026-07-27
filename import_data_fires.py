import requests
import geopandas as gpd
import numpy as np
import pandas as pd

# this dataset is:
# 'Fire Incident Locations - Historical'
def get_data():

    base_url = "https://delivery.maps.gov.bc.ca/arcgis/rest/services/mpcm/bcgwpub/MapServer/603/query"
    result_off_set = 0
    chunk_size = 500

    parameters = {
        # "where": "CURRENT_SIZE>=100 AND FIRE_YEAR>=1970",
        # "where": "CURRENT_SIZE>=100",
        "where": "1=1",
        # "orderByFields": "CURRENT_SIZE DESC",
        # "orderByFields": "FIRE_YEAR",
        "orderByFields": "OBJECTID ASC",
        # "orderByFields": "IGNITION_DATE",
        # "outFields": "LATITUDE,LONGITUDE,CURRENT_SIZE,FIRE_NUMBER,FIRE_YEAR,IGNITION_DATE,FIRE_OUT_DATE,FIRE_CAUSE",
        "outFields": "*",
        "f": "geojson",
        "resultRecordCount": chunk_size,
        "resultOffset": result_off_set
    }

    ls_data = []

    while True:
        
        parameters["resultOffset"] = result_off_set
        response = requests.get(base_url, params=parameters)
        data = response.json()
        
        features = data.get("features", [])
        if not features:
            break
        
        ls_data.extend(features)
        
        result_off_set += 1000  # can only query 1000 data entries at a time
        




    gdf = gpd.GeoDataFrame.from_features(ls_data, crs="EPSG:4326")
    

    gdf.to_file("raw_data/fires/forest_fires.geojson", driver="GeoJSON")
    gdf.to_csv("raw_data/fires/forest_fires_raw.csv", index=False)
    
    return gdf

# this dataset is:
# 'BC Wildfire Fire Perimeters - Historical'
def get_historical_fire_perimeters():

    base_url = (
        "https://delivery.maps.gov.bc.ca/arcgis/rest/services/"
        "whse/bcgw_pub_WHSE_LAND_AND_NATURAL_RESOURCE/"
        "MapServer/6/query"
    )

    chunk_size = 1000
    result_offset = 0
    all_features = []

    parameters = {
        # Retrieve every fire perimeter.
        "where": "1=1",

        # Retrieve every available attribute.
        "outFields": "*",

        # Include the actual polygon geometry.
        "returnGeometry": "true",

        # Return coordinates as longitude/latitude.
        "outSR": 4326,

        # Stable ordering is important for pagination.
        "orderByFields": "OBJECTID ASC",

        # Request GeoJSON instead of ArcGIS JSON.
        "f": "geojson",

        # Maximum number of records per request.
        "resultRecordCount": chunk_size,

        # Updated inside the loop.
        "resultOffset": result_offset,
    }

    while True:

        parameters["resultOffset"] = result_offset

        response = requests.get(
            base_url,
            params=parameters,
            timeout=120
        )
        if not response.ok:
            print("Status:", response.status_code)
            print("URL:", response.url)
            print("Server response:")
            print(response.text[:2000])


        response.raise_for_status()
        data = response.json()

        # ArcGIS can return an error inside an HTTP 200 response.
        if "error" in data:
            raise RuntimeError(data["error"])

        features = data.get("features", [])

        if not features:
            break

        all_features.extend(features)

        print(
            f"Downloaded {len(features)} records; "
            f"{len(all_features)} total"
        )

        # Begin the next request after the records just received.
        result_offset += len(features)

        # A partial page usually indicates that this was the final page.
        if len(features) < chunk_size:
            break

    gdf = gpd.GeoDataFrame.from_features(
        all_features,
        crs="EPSG:4326"
    )
    
    gdf.to_file("raw_data/fires/forest_fires_perimeter.geojson", driver="GeoJSON")
    gdf.to_csv("raw_data/fires/forest_fires_perimeter.csv", index=False)

    return gdf

get_data()
# get_historical_fire_perimeters()
# with 2000 constraint 1814
# with 1970 constraint, i.e. all data  3042
# no date constraint 4438

# no size or date constraint 

