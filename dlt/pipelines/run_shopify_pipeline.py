import dlt
import os
from sources.shopify_source import shopify_source

def run():
    
    pipeline = dlt.pipeline(
        pipeline_name="data",
        destination=dlt.destinations.duckdb("../data.duckdb"),
        dataset_name="shopify",
    )

    load_info = pipeline.run(shopify_source(), table_name="products")
    print("✅ Shopify pipeline finished!")

if __name__ == "__main__":
    run()
