
import geopandas as gpd
import pandas as pd

population_data = pd.read_csv('raw_data/municipalities/bc_municipality_populations.csv')
print(f'Number of unique cities in population dataset: {population_data['Region.Name'].nunique()}')
print(population_data.columns)

boundary_data = gpd.read_file('raw_data/municipalities/bc_municipality_boundaries.geojson')
# Index(['Region', 'Region.Name', 'Type', 'Year', 'Gender', 'Total'], dtype='str')
population_cols = ['Region.Name', 'Year', 'Total']
population_data = population_data[population_cols]
population_data = population_data.rename(columns={'Region.Name': 'MUNICIPALITY', 'Total': 'POPULATION'})

population_name_corrections = {
    "Fort St. James": "Fort St James",
    "Northern Rockies Regional Municipality": "NRRM",
    "Fort St. John": "Fort St John",
    "Langley, City of": "Langley - City",
    "Langley, District Municipality": "Langley - District",
    "Sun Peaks Mountain": "Sun Peaks",
    "Sechelt District Municipality": "Sechelt",
    "North Vancouver, District Municipality": "North Vancouver - District",
    "North Vancouver, City of": "North Vancouver - City",
}

population_data["MUNICIPALITY"] = (population_data["MUNICIPALITY"].replace(population_name_corrections))


# boundary_data = gpd.read_file('bc_municipality_boundaries.geojson')
print(f'Number of unique cities in boundary dataset: {boundary_data['ADMIN_AREA_ABBREVIATION'].nunique()}')

# print(boundary_data.columns)
# Index(['LGL_ADMIN_AREA_ID', 'ADMIN_AREA_NAME', 'ADMIN_AREA_ABBREVIATION',
#        'ADMIN_AREA_BOUNDARY_TYPE', 'ADMIN_AREA_GROUP_NAME',
#        'CHANGE_REQUESTED_ORG', 'UPDATE_TYPE', 'WHEN_UPDATED', 'MAP_STATUS',
#        'OIC_MO_NUMBER', 'OIC_MO_YEAR', 'OIC_MO_TYPE', 'WEBSITE_URL',
#        'IMAGE_URL', 'AFFECTED_ADMIN_AREA_ABRVN', 'FEATURE_AREA_SQM',
#        'FEATURE_LENGTH_M', 'OBJECTID', 'SE_ANNO_CAD_DATA', 'geometry'],
#       dtype='str')
boundary_cols = ['ADMIN_AREA_ABBREVIATION', 'geometry']
boundary_data = boundary_data[boundary_cols]
boundary_data = boundary_data.rename(columns={'ADMIN_AREA_ABBREVIATION': 'MUNICIPALITY'})

print(boundary_data)
print(population_data)

final_df = boundary_data.merge(population_data, how='left', on='MUNICIPALITY')

final_df.to_file("intermediate_data/municipalities_intermediate.geojson", driver="GeoJSON")
final_df.to_csv("intermediate_data/municipalities_intermediate.csv", index=False)

# municipality names that do not align, will deal with manually:
# bondaries --> population
# Fort St James --> Fort St. James
# NRRM --> Northern Rockies Regional Municipality
# Fort St John --> Fort St. John
# Langley - City --> Langley, City of
# Langley - District --> Langley, District Municipality
# Sun Peaks --> Sun Peaks Mountain
# Sechelt --> Sechelt District Municipality
# North Vancouver - District --> North Vancouver, District Municipality
# North Vancouver - City --> North Vancouver, City of
