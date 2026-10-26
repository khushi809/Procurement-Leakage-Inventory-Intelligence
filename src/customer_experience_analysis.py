
from pathlib import Path
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import mannwhitneyu

PROJECT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_DIR / "outputs" / "olist.db"
OUTPUT_DIR = PROJECT_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

query = """
SELECT
    o.order_id,
    o.order_status,
    o.order_delivered_customer_date,
    o.order_estimated_delivery_date,
    r.review_score
FROM orders AS o
INNER JOIN order_reviews AS r
    ON o.order_id = r.order_id
WHERE o.order_status = 'delivered'
"""

with sqlite3.connect(DB_PATH) as conn:
    df = pd.read_sql_query(query, conn)

# Parse dates
date_columns = [
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]
for column in date_columns:
    df[column] = pd.to_datetime(df[column], errors="coerce")

# Remove records that cannot support the comparison
df = df.dropna(
    subset=[
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
        "review_score",
    ]
).copy()

# A positive value means delivery happened after the estimate
df["delay_days"] = (
    df["order_delivered_customer_date"]
    - df["order_estimated_delivery_date"]
).dt.total_seconds() / 86400

df["delivery_group"] = df["delay_days"].gt(0).map({
    True: "Late",
    False: "On time or early",
})

summary = (
    df.groupby("delivery_group")
    .agg(
        orders=("order_id", "nunique"),
        average_review=("review_score", "mean"),
        median_review=("review_score", "median"),
        average_delay_days=("delay_days", "mean"),
    )
    .round(2)
)

print("\nDELIVERY AND CUSTOMER EXPERIENCE\n")
print(summary)

late_scores = df.loc[
    df["delivery_group"] == "Late", "review_score"
]
on_time_scores = df.loc[
    df["delivery_group"] == "On time or early", "review_score"
]

if len(late_scores) > 0 and len(on_time_scores) > 0:
    test = mannwhitneyu(
        late_scores,
        on_time_scores,
        alternative="two-sided",
    )

    print("\nMann–Whitney U test")
    print(f"U statistic: {test.statistic:.2f}")
    print(f"p-value: {test.pvalue:.6g}")

    if test.pvalue < 0.05:
        print(
            "The review-score distributions differ "
            "statistically at the 5% significance level."
        )
    else:
        print(
            "No statistically significant difference was "
            "detected at the 5% significance level."
        )

# Export reproducible results
summary.to_csv(
    OUTPUT_DIR / "customer_experience_summary.csv"
)

df.to_csv(
    OUTPUT_DIR / "customer_experience_detail.csv",
    index=False,
)

# Visualise the comparison
ax = summary["average_review"].plot(
    kind="bar",
    title="Average Review Score by Delivery Group",
    ylabel="Average review score (1–5)",
    xlabel="",
    ylim=(0, 5),
    rot=0,
)
plt.tight_layout()
plt.savefig(
    OUTPUT_DIR / "delivery_review_comparison.png",
    dpi=160,
)
plt.close()

print("\nSaved summary, detail data, and chart in outputs/.")
