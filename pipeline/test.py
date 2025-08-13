"""Generate dummy Shopify product data using SDV."""

from synthetic_data_generator import generate_synthetic_data, save_synthetic_data_to_duckdb

tables = ["shopify.products"]
db_path = "data.duckdb"
print(f"Generating synthetic data to {db_path}")

synthetic_data = generate_synthetic_data(
    tables=tables,
    db_path=db_path,
    num_rows=1000,
)
print(f"Generated {len(synthetic_data['shopify.products'])} rows of synthetic data")

save_synthetic_data_to_duckdb(
synthetic_data=synthetic_data,
db_path=db_path,
replace_existing=True,
)
print("✅ Generated and saved synthetic Shopify products data")