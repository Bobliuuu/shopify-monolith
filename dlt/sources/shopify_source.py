import dlt
import requests
import os


def shopify_api_get(endpoint):
    api_key = os.getenv('SHOPIFY_API_KEY')
    password = os.getenv('SHOPIFY_API_PASSWORD')
    shop_name = os.getenv('SHOPIFY_SHOP_NAME')

    url = f"https://{shop_name}.myshopify.com/admin/api/.../{endpoint}.json"
    response = requests.get(url, auth=(api_key, password))
    response.raise_for_status()
    return response.json()


@dlt.resource(name="shopify_products", write_disposition="replace")
def get_products():
    data = shopify_api_get("products")
    for item in data.get("products", []):
        yield item


@dlt.resource(name="shopify_orders", write_disposition="replace")
def get_orders():
    data = shopify_api_get("orders")
    for item in data.get("orders", []):
        yield item


@dlt.resource(name="shopify_customers", write_disposition="replace")
def get_customers():
    data = shopify_api_get("customers")
    for item in data.get("customers", []):
        yield item


@dlt.source
def shopify_source():
    yield get_products()
    yield get_orders()
    yield get_customers()
