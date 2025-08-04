import dlt
from sources.shopify_source import shopify_source

def run():
    pipeline = dlt.pipeline(
        pipeline_name="shopify_pipeline",
        destination="duckdb",
        dataset_name="src"
    )

    load_info = pipeline.run(shopify_source(), table_name="products")
    print("✅ Shopify pipeline finished!")
    print(load_info)

if __name__ == "__main__":
    run()
