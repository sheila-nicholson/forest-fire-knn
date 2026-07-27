import requests
import geopandas as gpd
import pandas as pd

def get_municipality_boundaries():
    base_url = "https://openmaps.gov.bc.ca/geo/pub/ows"

    parameters = {
        "service": "WFS",
        "version": "2.0.0",
        "request": "GetFeature",

        # Dataset name from package_show["result"]["resources"][...]["object_name"]
        "typeNames": "pub:WHSE_LEGAL_ADMIN_BOUNDARIES.ABMS_MUNICIPALITIES_SP",


        # Return actual attributes and polygon geometry.
        "outputFormat": "application/json",

        # Longitude/latitude coordinates.
        "srsName": "EPSG:4326",

        # Stable ordering.
        "sortBy": "OBJECTID",

        # Safely below the normal WFS maximum.
        "count": 1000,
    }

    response = requests.get(
        base_url,
        params=parameters,
        timeout=120,
    )

    response.raise_for_status()

    data = response.json()

    if "features" not in data:
        raise RuntimeError(
            "The WFS response did not contain GeoJSON features. "
            f"Response: {data}"
        )

    bc_municipality_boundaries = gpd.GeoDataFrame.from_features(
        data["features"],
        crs="EPSG:4326",
    )

    print(f"Downloaded {len(bc_municipality_boundaries):,} municipality boundaries")
    print(bc_municipality_boundaries.columns.tolist())

    return bc_municipality_boundaries

def get_municipality_populations():
    
    url = "https://catalogue.data.gov.bc.ca/dataset/86839277-986a-4a29-9f70-fa9b1166f6cb/resource/0e15d04d-127c-457a-b999-20800c929927/download/municipality-population.csv"

    cols = ['Region', 'Region.Name', 'Type', 'Year', 'Gender', 'Total']

    bc_municipality_populations = pd.read_csv(url)
    bc_municipality_populations = bc_municipality_populations[cols]
    
    print(bc_municipality_populations.shape[0])
    
    mask1 = bc_municipality_populations['Type'] == 'Estimate'
    mask2 = bc_municipality_populations['Gender'] == 'T'
    
    bc_municipality_populations = bc_municipality_populations[mask1 & mask2]
    print(bc_municipality_populations.shape[0])
    
    bc_municipality_populations.to_csv('raw_data/municipalities/bc_municipality_populations.csv', index=False)


get_municipality_populations()
bc_municipality_boundaries = get_municipality_boundaries()

bc_municipality_boundaries.to_file(
    "raw_data/municipalities/bc_municipality_boundaries.geojson",
    driver="GeoJSON",
)

bc_municipality_boundaries.to_csv(
    "raw_data/municipalities/bc_municipality_boundaries.csv",
    index=False,
)