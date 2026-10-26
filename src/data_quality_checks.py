
from pathlib import Path
import sqlite3
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_DIR / "outputs" / "olist.db"
OUTPUT_DIR = PROJECT_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

checks = []

def add_check(name, observed, expected, passed, note=""):
    checks.append({
        "check_name": name,
        "observed_value": observed,
        "expected_value": expected,
        "status": "PASS" if passed else "REVIEW",
        "note": note,
    })

with sqlite3.connect(DB_PATH) as conn:
    # Check that each order ID is unique in the orders table
    result = pd.read_sql_query("""
        SELECT
            COUNT(*) AS total_rows,
            COUNT(DISTINCT order_id) AS unique_orders
        FROM orders
    """, conn).iloc[0]

    add_check(
        "Orders primary key uniqueness",
        int(result["unique_orders"]),
        int(result["total_rows"]),
        result["total_rows"] == result["unique_orders"],
        "Each order should have one row in orders."
    )

    # Check for order items without a matching order
    orphan_items = pd.read_sql_query("""
        SELECT COUNT(*) AS orphan_count
        FROM order_items AS i
        LEFT JOIN orders AS o
            ON i.order_id = o.order_id
        WHERE o.order_id IS NULL
    """, conn).iloc[0, 0]

    add_check(
        "Order items with no matching order",
        int(orphan_items),
        0,
        orphan_items == 0,
        "Investigate unmatched order IDs."
    )

    # Check for invalid negative item prices
    negative_prices = pd.read_sql_query("""
        SELECT COUNT(*)
        FROM order_items
        WHERE price < 0
    """, conn).iloc[0, 0]

    add_check(
        "Negative item prices",
        int(negative_prices),
        0,
        negative_prices == 0,
        "Review negative values before financial analysis."
    )

    # Check seller IDs that don't match the seller table
    unknown_sellers = pd.read_sql_query("""
        SELECT COUNT(*)
        FROM order_items AS i
        LEFT JOIN sellers AS s
            ON i.seller_id = s.seller_id
        WHERE s.seller_id IS NULL
    """, conn).iloc[0, 0]

    add_check(
        "Order items with unknown sellers",
        int(unknown_sellers),
        0,
        unknown_sellers == 0,
        "Check seller reference integrity."
    )

report = pd.DataFrame(checks)
report.to_csv(OUTPUT_DIR / "data_quality_report.csv", index=False)

print("\nDATA QUALITY REPORT\n")
print(report.to_string(index=False))
print("\nSaved to outputs/data_quality_report.csv")
print(f"Checks passing: {(report['status'] == 'PASS').sum()}/{len(report)}")
