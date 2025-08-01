import pandas as pd
import random
from datetime import datetime, timedelta
import numpy as np
import uuid
import os
from faker import Faker

random.seed(42)
np.random.seed(42)
fake = Faker('en_CA')

num_rows = 3000
output_dir = "shopify_data"
os.makedirs(output_dir, exist_ok=True)

products = [
    {"title": "Gift Card", "price": 10.00},
    {"title": "Selling Plans Ski Wax", "price": 9.95},
    {"title": "The 3p Fulfilled Snowboard", "price": 2629.95},
    {"title": "The Collection Snowboard: Hydrogen", "price": 600.00},
    {"title": "The Collection Snowboard: Liquid", "price": 749.95},
    {"title": "The Collection Snowboard: Oxygen", "price": 1025.00},
    {"title": "The Conquer at Price Snowboard", "price": 765.95},
    {"title": "The Conquist Snowboard", "price": 689.95},
    {"title": "The Inventory Not Tracked Snowboard", "price": 949.95},
    {"title": "The Multi-section Snowboard", "price": 729.95},
    {"title": "The Multi-managed Snowboard", "price": 629.95},
    {"title": "The Out of Stock Snowboard", "price": 685.95},
    {"title": "The Videogrpaher Snowboard", "price": 485.95},
]

customers = []
for i in range(num_rows):
    profile = fake.simple_profile()
    created = datetime(2022, 1, 1) + timedelta(days=random.randint(0, 900))
    customers.append({
        "customer_id": str(uuid.uuid4()),
        "first_name": profile["name"].split()[0],
        "last_name": profile["name"].split()[-1],
        "email": profile["mail"],
        "created_at": created,
        "phone_number": fake.phone_number(),
        "email_address": profile["mail"],
        "total_spent": 0.0,
        "orders_count": 0,
        "state": random.choice(["active", "inactive"])
    })
df_customers = pd.DataFrame(customers)

product_variants = []
for p in products:
    for _ in range(250):
        product_variants.append({
            "product_id": str(uuid.uuid4()),
            "title": p["title"],
            "vendor": "SnowboardCo",
            "product_type": "Snowboard" if "Snowboard" in p["title"] else "Accessory",
            "created_at": datetime(2021, 1, 1) + timedelta(days=random.randint(0, 1000)),
            "published_at": datetime(2022, 1, 1),
            "status": "active"
        })
df_products = pd.DataFrame(product_variants[:num_rows])

orders = []
sessions = []
refunds = []

for i in range(num_rows):
    customer = random.choice(customers)
    order_id = str(uuid.uuid4())
    order_date = customer["created_at"] + timedelta(days=random.randint(0, 365))
    product = random.choice(products)
    price = product["price"]
    fulfilled = random.choice(["fulfilled", "unfulfilled"])

    orders.append({
        "order_id": order_id,
        "created_at": order_date,
        "total_price": price,
        "currency": "CAD",
        "fulfillment_status": fulfilled,
        "customer_id": customer["customer_id"],
        "shipping_address": fake.address().replace("\n", ", ")
    })

    df_customers.loc[df_customers["customer_id"] == customer["customer_id"], "total_spent"] += price
    df_customers.loc[df_customers["customer_id"] == customer["customer_id"], "orders_count"] += 1

    sessions.append({
        "session_id": str(uuid.uuid4()),
        "customer_id": customer["customer_id"],
        "started_at": order_date - timedelta(minutes=random.randint(10, 120)),
        "ended_at": order_date,
        "device_type": random.choice(["mobile", "desktop", "tablet"]),
        "landing_page": "/products",
        "exit_page": "/checkout",
        "referrer": random.choice(["google.com", "facebook.com", "direct"]),
        "cart_value": price,
        "purchased": True,
        "order_id": order_id
    })

    if random.random() < 0.05:
        refunds.append({
            "refund_id": str(uuid.uuid4()),
            "order_id": order_id,
            "created_at": order_date + timedelta(days=random.randint(1, 10)),
            "refund_line_items": product["title"],
            "transactions": price
        })

df_orders = pd.DataFrame(orders)
df_sessions = pd.DataFrame(sessions)
df_refunds = pd.DataFrame(refunds)

inventory = []
for i in range(num_rows):
    inventory.append({
        "inventory_item_id": str(uuid.uuid4()),
        "available": random.randint(0, 100),
        "location_id": random.randint(1, 5),
        "updated_at": datetime.now() - timedelta(days=random.randint(0, 30))
    })
df_inventory = pd.DataFrame(inventory)

df_customers.to_csv(f"{output_dir}/customers_base.csv", index=False)
df_products.to_csv(f"{output_dir}/products_base.csv", index=False)
df_orders.to_csv(f"{output_dir}/orders_base.csv", index=False)
df_sessions.to_csv(f"{output_dir}/sessions_base.csv", index=False)
df_inventory.to_csv(f"{output_dir}/inventory_base.csv", index=False)
df_refunds.to_csv(f"{output_dir}/refunds_base.csv", index=False)

import zipfile
with zipfile.ZipFile(f"{output_dir}.zip", "w") as zipf:
    for file in os.listdir(output_dir):
        zipf.write(os.path.join(output_dir, file), arcname=file)
