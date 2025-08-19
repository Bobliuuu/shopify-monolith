import dlt
import requests
import os

def google_ads_api_get(resource):
    access_token = os.getenv("GOOGLE_ADS_ACCESS_TOKEN")
    customer_id = os.getenv("GOOGLE_ADS_CUSTOMER_ID")
    base_url = f"https://googleads.googleapis.com/v13/customers/{customer_id}/{resource}"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "developer-token": os.getenv("GOOGLE_ADS_DEV_TOKEN"),
    }

    response = requests.get(base_url, headers=headers)
    response.raise_for_status()
    return response.json()

@dlt.resource(name="google_ads_campaigns", write_disposition="replace")
def get_campaigns():
    # You may need to change this if the resource isn't exposed directly
    data = google_ads_api_get("campaigns")
    for item in data.get("results", []):
        yield item

@dlt.source
def google_ads_source():
    yield get_campaigns()
