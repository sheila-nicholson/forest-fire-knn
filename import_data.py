import requests
import geopandas as gpd
import numpy as np
import pandas as pd

def get_data():

    base_url = "https://delivery.maps.gov.bc.ca/arcgis/rest/services/mpcm/bcgwpub/MapServer/603/query"
    result_off_set = 0
    page_size = 1000

    parameters = {
        # "where": "CURRENT_SIZE>=100 AND FIRE_YEAR>=1970",
        "where": "CURRENT_SIZE>=1000",
        # "where": "1=1",
        # "orderByFields": "CURRENT_SIZE DESC",
        # "orderByFields": "FIRE_YEAR",
        "orderByFields": "IGNITION_DATE",
        "outFields": "LATITUDE,LONGITUDE,CURRENT_SIZE,FIRE_NUMBER,FIRE_YEAR,IGNITION_DATE,FIRE_OUT_DATE,FIRE_CAUSE",
        # "outFields": "*",
        "f": "geojson",
        "resultRecordCount": page_size,
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

    gdf = gpd.GeoDataFrame.from_features(ls_data)
    
    # deal with time and dates - consider using UTC format - are the time zones all the same??
    gdf['IGNITION_DATE'] = pd.to_datetime(gdf['IGNITION_DATE'], unit = 'ms', origin='unix')
    gdf['FIRE_OUT_DATE'] = pd.to_datetime(gdf['FIRE_OUT_DATE'], unit = 'ms', origin='unix')
    
    fire_centres = {
        "C": "Cariboo Fire Centre",
        "V": "Costal Fire Centre",
        "K": "Kamloops Fire Centre",
        "R": "Northwest Fire Centre",
        "G": "Prince George Fire Centre",
        "N": "Southeast Fire Centre"
    }
    # TODO: create dictionary for all fire zones

    gdf['FIRE_CENTRE'] = (
        gdf['FIRE_NUMBER']
        .astype(str)
        .str[0]
        .map(fire_centres)
    )
        
            
    gdf.to_html("data.html")
    gdf.to_csv("data.csv")
    
    return gdf

# get_data()
# with 2000 constraint 1814
# with 1970 constraint, i.e. all data  3042
# no date constraint 4438

# no size or date constraint 

