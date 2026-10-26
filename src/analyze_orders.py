
from pathlib import Path
import pandas as pd

# Project paths
PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "sheets"
OUTPUT_DIR = PROJECT_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

print("=" * 60)
print("E-COMMERCE BUSINESS PERFORMANCE ANALYSIS")
print("=" * 60)

# Load the required datasets
orders = pd.read_csv(DATA_DIR / "olist_orders_dataset.csv")
items = pd.read_csv(DATA_DIR / "olist_order_items_dataset.csv")
payments = pd.read_csv(DATA_DIR / "olist_order_payments_dataset.csv")

# Convert date columns to datetime
date_columns = [
    "order_purchase_timestamp",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]

for column in date_columns:
    orders[column] = pd.to_datetime(orders[column], errors="coerce")

# Calculate sales and freight by order
order_financials = (
    items.groupby("order_id", as_index=False)
    .agg(
        item_sales=("price", "sum"),
        freight_cost=("freight_value", "sum"),
        item_count=("order_item_id", "count"),
    )
)

# Combine order, financial and payment data
analysis = orders.merge(
    order_financials, on="order_id", how="left"
)

payment_totals = (
    payments.groupby("order_id", as_index=False)
    .agg(payment_value=("payment_value", "sum"))
)

analysis = analysis.merge(
    payment_totals, on="order_id", how="left"
)

# Calculate delivery time and delay
analysis["delivery_days"] = (
    analysis["order_delivered_customer_date"]
    - analysis["order_purchase_timestamp"]
).dt.total_seconds() / 86400

analysis["delivery_delay_days"] = (
    analysis["order_delivered_customer_date"]
    - analysis["order_estimated_delivery_date"]
).dt.total_seconds() / 86400

# A positive delay means delivery was later than estimated
analysis["delivered_late"] = (
    analysis["delivery_delay_days"] > 0
)

# Print business KPIs
delivered = analysis[
    analysis["order_status"] == "delivered"
].copy()

total_orders = len(analysis)
delivered_orders = len(delivered)
late_orders = int(delivered["delivered_late"].sum())

sales = analysis["item_sales"].sum()
freight = analysis["freight_cost"].sum()
payments_total = analysis["payment_value"].sum()

print(f"\nTotal orders: {total_orders:,}")
print(f"Delivered orders: {delivered_orders:,}")
print(f"Item sales value: R$ {sales:,.2f}")
print(f"Freight charges: R$ {freight:,.2f}")
print(f"Recorded payment value: R$ {payments_total:,.2f}")

if delivered_orders:
    print(
        f"Average delivery time: "
        f"{delivered['delivery_days'].mean():.2f} days"
    )
    print(
        f"Late deliveries: {late_orders:,} "
        f"({late_orders / delivered_orders:.1%})"
    )

# Save the analysis dataset for later Excel and Power BI work
output_file = OUTPUT_DIR / "order_analysis.csv"
analysis.to_csv(output_file, index=False)

print(f"\nAnalysis dataset saved to: {output_file}")
print("\nAnalysis complete.")
