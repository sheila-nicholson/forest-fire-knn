import requests

meta_url = "https://delivery.maps.gov.bc.ca/arcgis/rest/services/mpcm/bcgwpub/MapServer/603"
res = requests.get(meta_url, params={"f":"json"})
metadata = res.json()

for field in metadata["fields"]:
    print(field["name"], field.get("domain"))