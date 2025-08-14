import dlt
import requests
import os

def notion_api_post(payload):
    notion_token = os.getenv("NOTION_API_KEY")
    database_id = os.getenv("NOTION_DATABASE_ID")

    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()

@dlt.resource(name="notion_pages", write_disposition="replace")
def get_notion_data():
    data = notion_api_post({})
    for item in data.get("results", []):
        yield item

@dlt.source
def notion_source():
    yield get_notion_data()
