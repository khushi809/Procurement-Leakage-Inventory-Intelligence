
from pathlib import Path
import sqlite3
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_DIR / "outputs" / "olist.db"
SQL_PATH = PROJECT_DIR / "sql" / "seller_performance.sql"
OUTPUT_DIR = PROJECT_DIR / "outputs"

query = SQL_PATH.read_text(encoding="utf-8")

with sqlite3.connect(DB_PATH) as connection:
    results = pd.read_sql_query(query, connection)

print("\nTOP 20 SELLERS BY ITEM SALES\n")
print(results.to_string(index=False))

output_file = OUTPUT_DIR / "seller_performance.csv"
results.to_csv(output_file, index=False)

print(f"\nResults saved to: {output_file}")
