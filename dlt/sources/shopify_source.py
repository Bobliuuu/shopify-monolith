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


@dlt.resource(name="shopify_orders", write_disposition="replace")
def get_orders():
    # Define explicit schema to prevent dlt from auto-inferring types
    schema = {
        "id": "string",
        "name": "string",
        "email": "string", 
        "phone": "string",
        "created_at": "timestamp",
        "updated_at": "timestamp",
        "processed_at": "timestamp",
        "cancelled_at": "timestamp",
        "cancel_reason": "string",
        "total_price_set": "json",
        "subtotal_price_set": "json",
        "total_tax_set": "json",
        "total_shipping_price_set": "json",
        "customer": "json",
        "shipping_address": "json",
        "billing_address": "json",
        "line_items": "json"
    }
    
    # Set the schema for this resource
    dlt.current.resource().set_schema(schema)
    query = """
    query GetOrders($first: Int!) {
        orders(first: $first) {
            edges {
                node {
                    id
                    name
                    email
                    phone
                    createdAt
                    updatedAt
                    processedAt
                    cancelledAt
                    cancelReason
                    totalPriceSet {
                        shopMoney {
                            amount
                            currencyCode
                        }
                    }
                    subtotalPriceSet {
                        shopMoney {
                            amount
                            currencyCode
                        }
                    }
                    totalTaxSet {
                        shopMoney {
                            amount
                            currencyCode
                        }
                    }
                    totalShippingPriceSet {
                        shopMoney {
                            amount
                            currencyCode
                        }
                    }
                    customer {
                        id
                        firstName
                        lastName
                        email
                    }
                    shippingAddress {
                        address1
                        address2
                        city
                        province
                        country
                        zip
                        phone
                    }
                    billingAddress {
                        address1
                        address2
                        city
                        province
                        country
                        zip
                        phone
                    }
                    lineItems(first: 100) {
                        edges {
                            node {
                                id
                                title
                                quantity
                                sku
                                variant {
                                    id
                                    title
                                    sku
                                    price
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    """
    
    variables = {"first": 100}
    data = shopify_graphql_query(query, variables)
    
    for edge in data.get("data", {}).get("orders", {}).get("edges", []):
        order = edge["node"]
        
        # Ensure ID fields are explicitly strings to prevent INT64 conversion
        if "id" in order:
            order["id"] = str(order["id"])
        
        # Convert customer ID
        if "customer" in order and order["customer"] and "id" in order["customer"]:
            order["customer"]["id"] = str(order["customer"]["id"])
        
        # Convert line item IDs
        if "lineItems" in order and "edges" in order["lineItems"]:
            for line_item_edge in order["lineItems"]["edges"]:
                line_item = line_item_edge["node"]
                if "id" in line_item:
                    line_item["id"] = str(line_item["id"])
                if "variant" in line_item and line_item["variant"] and "id" in line_item["variant"]:
                    line_item["variant"]["id"] = str(line_item["variant"]["id"])
        
        yield order


@dlt.resource(name="shopify_customers", write_disposition="replace")
def get_customers():
    # Define explicit schema to prevent dlt from auto-inferring types
    schema = {
        "id": "string",
        "first_name": "string",
        "last_name": "string",
        "email": "string",
        "phone": "string",
        "accepts_marketing": "boolean",
        "created_at": "timestamp",
        "updated_at": "timestamp",
        "orders_count": "integer",
        "total_spent": "string",
        "note": "string",
        "tags": "string",
        "default_address": "json",
        "addresses": "json"
    }
    
    # Set the schema for this resource
    dlt.current.resource().set_schema(schema)
    query = """
    query GetCustomers($first: Int!) {
        customers(first: $first) {
            edges {
                node {
                    id
                    firstName
                    lastName
                    email
                    phone
                    acceptsMarketing
                    createdAt
                    updatedAt
                    ordersCount
                    totalSpent
                    note
                    tags
                    defaultAddress {
                        address1
                        address2
                        city
                        province
                        country
                        zip
                        phone
                    }
                    addresses {
                        address1
                        address2
                        city
                        province
                        country
                        zip
                        phone
                    }
                }
            }
        }
    }
    """
    
    variables = {"first": 100}
    data = shopify_graphql_query(query, variables)
    
    for edge in data.get("data", {}).get("customers", {}).get("edges", []):
        customer = edge["node"]
        
        # Ensure ID fields are explicitly strings to prevent INT64 conversion
        if "id" in customer:
            customer["id"] = str(customer["id"])
        
        yield customer


@dlt.source
def shopify_source():
    yield get_products()
