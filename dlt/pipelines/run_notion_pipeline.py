import dlt
from sources.notion_source import notion_source

def run():
    pipeline = dlt.pipeline(
        pipeline_name="notion_pipeline",
        destination="postgres",
        dataset_name="notion_data"
    )

    load_info = pipeline.run(notion_source())
    print("✅ Notion pipeline finished!")
    print(load_info)

if __name__ == "__main__":
    run()
