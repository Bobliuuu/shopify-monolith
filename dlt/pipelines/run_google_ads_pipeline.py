import dlt
from sources.google_ads_source import google_ads_source

def run():
    pipeline = dlt.pipeline(
        pipeline_name="google_ads_pipeline",
        destination="postgres",
        dataset_name="google_ads_data"
    )

    load_info = pipeline.run(google_ads_source())
    print("✅ Google Ads pipeline finished!")
    print(load_info)

if __name__ == "__main__":
    run()
