import requests
import geopandas as gpd
import numpy as np

base_url = "https://delivery.maps.gov.bc.ca/arcgis/rest/services/mpcm/bcgwpub/MapServer/603/query"
result_off_set = 0
page_size = 1000

parameters = {
    "where": "CURRENT_SIZE>=100 AND FIRE_YEAR>=2000",
    #"orderByFields": "CURRENT_SIZE DESC",
    "orderByFields": "FIRE_YEAR",
    "outFields": "LATITUDE,LONGITUDE,CURRENT_SIZE,FIRE_NUMBER,FIRE_YEAR,RESPONSE_TYPE_DESC,FIRE_TYPE",
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
    
    result_off_set += 1000

# print(ls_data)

gdf = gpd.GeoDataFrame.from_features(ls_data)
gdf.to_html("data.html")
gdf.to_csv("data.csv")
