import os
from pathlib import Path
import re
import duckdb
import pandas as pd
from sdv.metadata import SingleTableMetadata
from sdv.single_table import GaussianCopulaSynthesizer

UUID_RE = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$")

def _infer_sdtype(col, dtype, sample: pd.Series) -> str:
    """Heuristics mapping DuckDB type + sample data -> SDV sdtype."""
    t = dtype.upper()

    # Datetime / date
    if any(x in t for x in ["TIMESTAMP", "DATE", "TIME"]):
        return "datetime"

    # Boolean
    if "BOOL" in t:
        return "boolean"

    # Numeric (ints vs floats/decimals) - SDV uses 'numerical' for all numbers
    if any(x in t for x in ["TINYINT", "SMALLINT", "INTEGER", "BIGINT", "HUGEINT", "UBIGINT", "UINTEGER", "DOUBLE", "REAL", "FLOAT", "DECIMAL", "NUMERIC"]):
        return "numerical"

    # UUID
    if "UUID" in t:
        return "id"
    if col.lower().endswith("_id") or col.lower() == "id":
        # If it looks like an id (uuid-ish or high-cardinality), treat as id
        head = sample.dropna().astype(str).head(200)
        if len(head) > 0 and (head.map(lambda v: bool(UUID_RE.match(v))).mean() > 0.5 or head.nunique()/max(1,len(head)) > 0.9):
            return "id"

    # Text vs categorical (low cardinality)
    head = sample.dropna().astype(str)
    nunique = head.nunique()
    ratio = nunique / max(1, len(head))
    if nunique <= 1000 and ratio <= 0.2:   # tweak thresholds if needed
        return "categorical"

    return "text"

def build_metadata_from_duckdb(con: duckdb.DuckDBPyConnection, table: str, sample_limit: int = 100_000):
    """
    Pull schema via PRAGMA, load a sample (or full) table, and construct SDV SingleTableMetadata with
    best-guess sdtypes and a couple common constraints.
    """
    # 1) Get columns & types
    # PRAGMA table_info returns columns like: column_name, column_type, null, key, default (duckdb)
    ti = con.execute(f"PRAGMA table_info('{table}')").df()
    # Be robust to name variants across versions
    col_name_col = next(c for c in ti.columns if c.lower() in ["column_name", "name"])
    col_type_col = next(c for c in ti.columns if c.lower() in ["column_type", "type"])
    pk_col = next((c for c in ti.columns if c.lower() in ["primary_key", "pk", "key"]), None)

    cols = ti[[col_name_col, col_type_col] + ([pk_col] if pk_col else [])]
    cols.columns = ["column_name", "column_type"] + (["pk"] if pk_col else [])

    # 2) Load data (SDV learns distributions from actual data)
    df = con.execute(f"SELECT * FROM {table} LIMIT {sample_limit}").df()

    # 3) Build metadata and override sdtypes
    meta = SingleTableMetadata()
    # Let SDV auto-detect basics first
    meta.detect_from_dataframe(data=df)

    # Re-infer per-column sdtype using DuckDB types + sample
    for _, r in cols.iterrows():
        c = r["column_name"]
        if c not in df.columns:
            continue
        sdtype = _infer_sdtype(c, r["column_type"], df[c])
        meta.update_column(c, sdtype=sdtype)

    # 4) Primary key (from schema if present; else infer unique id)
    if "pk" in cols.columns and (cols["pk"] == 1).any():
        pk = cols.loc[cols["pk"] == 1, "column_name"].iloc[0]
        meta.set_primary_key(pk)
    else:
        # If there's a unique-looking id column, mark it as PK
        for guess in ["id", "product_id", "uuid"]:
            if guess in df.columns and df[guess].notna().all() and df[guess].nunique() == len(df):
                meta.update_column(guess, sdtype="id")
                meta.set_primary_key(guess)
                break

    return meta, df

def generate_synthetic_data(tables: list, db_path: str = "data.duckdb", num_rows: int = 1000):
    """
    Generate synthetic data for specified tables using SDV.
    
    Args:
        tables: List of table names (e.g., ["shopify.products", "shopify.orders"])
        db_path: Path to DuckDB database
        num_rows: Number of synthetic rows to generate per table
    
    Returns:
        dict: Dictionary with table names as keys and synthetic DataFrames as values
    """
    if not os.path.isabs(db_path):
        db_path = str((Path(__file__).resolve().parent.parent.parent / db_path).resolve())

    print(f"Generating synthetic data to {db_path}")

    con = duckdb.connect(db_path)
    synthetic_data = {}
    
    for table in tables:
        try:
            print(f"Processing table: {table}")
            
            # Build metadata and get seed data
            metadata, df_seed = build_metadata_from_duckdb(con, table)
            
            # Ensure pandas dtypes are good for SDV (timestamps become datetime64)
            for col, sdtype in (metadata.to_dict()["columns"]).items():
                if sdtype.get("sdtype") == "datetime":
                    df_seed[col] = pd.to_datetime(df_seed[col], errors="coerce")
            
            # Create synthesizer and fit
            synth = GaussianCopulaSynthesizer(metadata, enforce_rounding=False)
            synth.fit(df_seed)
            
            # Generate synthetic data
            df_synth = synth.sample(num_rows=num_rows)
            synthetic_data[table] = df_synth
            
            print(f"✅ Generated {num_rows} synthetic rows for {table}")
            
        except Exception as e:
            print(f"❌ Error processing table {table}: {str(e)}")
            synthetic_data[table] = None
    
    con.close()
    return synthetic_data

def save_synthetic_data_to_duckdb(synthetic_data: dict, db_path: str = "data.duckdb", replace_existing: bool = True):
    """
    Save synthetic data back to DuckDB database.
    
    Args:
        synthetic_data: Dictionary with table names as keys and synthetic DataFrames as values
        db_path: Path to DuckDB database
        replace_existing: Whether to replace existing tables or append
    """
    if not os.path.isabs(db_path):
        db_path = str((Path(__file__).resolve().parent / db_path).resolve())

    con = duckdb.connect(db_path)
    
    for table_name, df in synthetic_data.items():
        if df is not None:
            try:
                # Extract just the table name without schema
                if '.' in table_name:
                    schema, table = table_name.split('.', 1)
                    full_table_name = f"{schema}.{table}"
                else:
                    full_table_name = table_name
                
                if replace_existing:
                    # Drop existing table if it exists
                    con.execute(f"DROP TABLE IF EXISTS {full_table_name}")
                
                # Create table and insert data
                con.execute(f"CREATE TABLE {full_table_name} AS SELECT * FROM df")
                print(f"✅ Saved synthetic data to {full_table_name}")

                
            except Exception as e:
                print(f"❌ Error saving table {table_name}: {str(e)}")
    
    con.close()

def main():
    """Main function for standalone execution"""
    # Default tables to process
    default_tables = ["shopify.products"]
    
    # Generate synthetic data
    synthetic_data = generate_synthetic_data(default_tables)
    
    # Save to DuckDB
    save_synthetic_data_to_duckdb(synthetic_data)
    
    # Also save to CSV for reference
    for table_name, df in synthetic_data.items():
        if df is not None:
            csv_filename = f"synthetic_{table_name.replace('.', '_')}.csv"
            df.to_csv(csv_filename, index=False)
            print(f"✅ Saved CSV: {csv_filename}")

if __name__ == "__main__":
    main()
