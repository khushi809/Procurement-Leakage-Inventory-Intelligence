
from pathlib import Path
import sqlite3
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "sheets"
OUTPUT_DIR = PROJECT_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

DB_PATH = OUTPUT_DIR / "olist.db"

# Load the tables needed for our business analysis.
files = {
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
    "order_reviews": "olist_order_reviews_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "products": "olist_products_dataset.csv",
    "customers": "olist_customers_dataset.csv",
}

with sqlite3.connect(DB_PATH) as connection:
    for table_name, file_name in files.items():
        file_path = DATA_DIR / file_name

        if not file_path.exists():
            print(f"Missing file: {file_name}")
            continue

        df = pd.read_csv(file_path)

        df.to_sql(
            table_name,
            connection,
            if_exists="replace",
            index=False
        )

        print(
            f"Loaded {table_name}: "
            f"{len(df):,} rows"
        )

    print("\nDatabase tables:")
    tables = pd.read_sql_query(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        ORDER BY name;
        """,
        connection
    )

    print(tables.to_string(index=False))

print(f"\nDatabase saved at: {DB_PATH}")
