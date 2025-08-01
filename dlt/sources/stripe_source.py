import dlt
import requests
import os

def stripe_api_get(endpoint):
    base_url = "https://api.stripe.com/v1"
    api_key = os.getenv("STRIPE_API_KEY")

    url = f"{base_url}/{endpoint}"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


@dlt.resource(name="stripe_customers", write_disposition="replace")
def get_customers():
    data = stripe_api_get("customers")
    for item in data.get("data", []):
        yield item


@dlt.resource(name="stripe_charges", write_disposition="replace")
def get_charges():
    data = stripe_api_get("charges")
    for item in data.get("data", []):
        yield item


@dlt.resource(name="stripe_invoices", write_disposition="replace")
def get_invoices():
    data = stripe_api_get("invoices")
    for item in data.get("data", []):
        yield item


@dlt.source
def stripe_source():
    yield get_customers()
    yield get_charges()
    yield get_invoices()
