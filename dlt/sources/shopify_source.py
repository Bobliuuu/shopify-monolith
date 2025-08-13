import dlt
import requests
import os
import dotenv
from dlt.pipeline import current

dotenv.load_dotenv()

def shopify_graphql_query(query, variables=None):
    """Execute a GraphQL query against Shopify Admin API"""
    api_key = os.getenv('SHOPIFY_API_KEY')
    password = os.getenv('SHOPIFY_API_PASSWORD')
    shop_name = os.getenv('SHOPIFY_SHOP_NAME')
    version = '2025-07'

    url = f"https://{shop_name}.myshopify.com/admin/api/{version}/graphql.json"
    
    headers = {
        'Content-Type': 'application/json',
        'X-Shopify-Access-Token': password
    }
    
    payload = {
        'query': query,
        'variables': variables or {}
    }
    
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()

# Define explicit schema to prevent dlt from auto-inferring types

@dlt.resource(
    name="shopify_products",
    write_disposition="replace",
    columns={
        "id": {"data_type": "text", "nullable": False},
        "title": {"data_type": "text", "nullable": True},
        "bodyHtml": {"data_type": "text", "nullable": True},
        "vendor": {"data_type": "text", "nullable": True},
        "productType": {"data_type": "text", "nullable": True},
        "createdAt": {"data_type": "timestamp", "nullable": False},
        "updatedAt": {"data_type": "timestamp", "nullable": False},
        "publishedAt": {"data_type": "timestamp", "nullable": True},
        "tags": {"data_type": "text", "nullable": True},
        "status": {"data_type": "text", "nullable": True},
        "handle": {"data_type": "text", "nullable": True},
        "templateSuffix": {"data_type": "text", "nullable": True},
        "featuredImage": {"data_type": "json", "nullable": True},  # Nested structure
        "variants": {"data_type": "json", "nullable": True},       # Nested
        "images": {"data_type": "json", "nullable": True},         # Nested
        "options": {"data_type": "json", "nullable": True},        # Nested
    }
)

def get_products():
    query = """
    query GetProducts($first: Int!) {
    products(first: $first) {
        edges {
            node {
                id
                title
                bodyHtml
                vendor
                productType
                createdAt
                handle
                updatedAt
                publishedAt
                templateSuffix
                tags
                status

                options {
                    id
                    name
                    position
                    values
                }

                variants(first: 100) {
                    edges {
                        node {
                            id
                            title
                            price
                            position
                            inventoryPolicy
                            compareAtPrice
                            createdAt
                            updatedAt
                            taxable
                            barcode
                            sku
                            image {
                                id
                            }
                            selectedOptions {
                                name
                                value
                            }
                        }
                    }
                }

                images(first: 100) {
                    edges {
                        node {
                        id
                        altText
                        originalSrc
                        width
                        height
                        }
                    }
                }

                featuredImage {
                    id
                    altText
                    originalSrc
                    width
                    height
                }
            }
        }
    }
}
"""
    
    variables = {"first": 100}
    data = shopify_graphql_query(query, variables)
    print(data)

    for edge in data.get("data", {}).get("products", {}).get("edges", []):
        yield edge["node"]

@dlt.source
def shopify_source():
    yield get_products()
