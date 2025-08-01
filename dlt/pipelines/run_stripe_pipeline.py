import dlt
from sources.stripe_source import stripe_source

def run():
    pipeline = dlt.pipeline(
        pipeline_name="stripe_pipeline",
        destination="postgres",
        dataset_name="stripe_data"
    )

    load_info = pipeline.run(stripe_source())
    print("✅ Stripe pipeline finished!")
    print(load_info)

if __name__ == "__main__":
    run()
