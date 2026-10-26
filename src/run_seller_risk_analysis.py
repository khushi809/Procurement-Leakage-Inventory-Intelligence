
from pathlib import Path
import sqlite3
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_DIR / "outputs" / "olist.db"
SQL_PATH = PROJECT_DIR / "sql" / "seller_risk_analysis.sql"
OUTPUT_PATH = PROJECT_DIR / "outputs" / "seller_risk_analysis.csv"

# Read the SQL query
with open(SQL_PATH, "r", encoding="utf-8") as file:
    query = file.read()

# Execute against SQLite and export results
with sqlite3.connect(DB_PATH) as connection:
    df = pd.read_sql_query(query, connection)

df.to_csv(OUTPUT_PATH, index=False)

print("SELLER RISK ANALYSIS")
print("-" * 50)
print(f"Sellers analysed: {len(df)}")
print(f"High-priority sellers: {(df['investigation_category'] == 'High priority investigation').sum()}")
print(f"Sellers requiring review: {(df['investigation_category'] == 'Review recommended').sum()}")

print("\nTop 10 sellers to investigate:")
print(
    df[
        [
            "seller_id",
            "total_orders",
            "total_sales",
            "freight_to_sales_pct",
            "late_delivery_pct",
            "avg_review_score",
            "risk_flag_count",
            "investigation_category",
        ]
    ].head(10).to_string(index=False)
)

print(f"\nResults saved to: {OUTPUT_PATH}")

