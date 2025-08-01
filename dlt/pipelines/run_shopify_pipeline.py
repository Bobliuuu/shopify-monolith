import dlt
from sources.shopify_source import shopify_source

def run():
    pipeline = dlt.pipeline(
        pipeline_name="shopify_pipeline",
        destination="postgres",
        dataset_name="shopify_data"
    )

    load_info = pipeline.run(shopify_source())
    print("✅ Shopify pipeline finished!")
    print(load_info)

if __name__ == "__main__":
    run()
