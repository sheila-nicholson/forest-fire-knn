import requests

CKAN_BASE = "https://catalogue.data.gov.bc.ca/api/3/action"

def get_data(package_name):
    resp = requests.get(f"{CKAN_BASE}/package_show", params={"id": package_name})
    resp.raise_for_status()
    return resp.json()["result"]["resources"]


# resources = get_data("bc-wildfire-fire-incident-locations-historical")

resources = get_data("bc-wildfire-fire-perimeters-historical")

for r in resources:
    print(r["name"])
    print("format:", r["format"])
    print("url:", r["url"])
    print()