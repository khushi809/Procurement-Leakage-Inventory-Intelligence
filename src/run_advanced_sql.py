
from pathlib import Path
import sqlite3
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_DIR / "outputs" / "olist.db"
SQL_PATH = PROJECT_DIR / "sql" / "advanced_seller_analysis.sql"
OUTPUT_DIR = PROJECT_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

query = SQL_PATH.read_text(encoding="utf-8")

with sqlite3.connect(DB_PATH) as connection:
    results = pd.read_sql_query(query, connection)

output_file = OUTPUT_DIR / "advanced_seller_analysis.csv"
results.to_csv(output_file, index=False)

print("\nADVANCED SELLER PERFORMANCE ANALYSIS")
print(f"Seller-month records: {len(results):,}")
print("\nMost recent monthly records:")
print(results.head(15).to_string(index=False))
print(f"\nFull results saved to: {output_file}")
