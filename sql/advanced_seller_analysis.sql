
-- Advanced Seller Performance Analysis
-- Business question:
-- Which sellers lead monthly sales, and how does performance change?

WITH monthly_seller_sales AS (
    SELECT
        oi.seller_id,
        strftime(
            '%Y-%m',
            o.order_purchase_timestamp
        ) AS sales_month,
        COUNT(DISTINCT o.order_id) AS total_orders,
        SUM(oi.price) AS item_sales,
        SUM(oi.freight_value) AS freight_cost
    FROM orders AS o
    INNER JOIN order_items AS oi
        ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
      AND o.order_purchase_timestamp IS NOT NULL
    GROUP BY
        oi.seller_id,
        strftime('%Y-%m', o.order_purchase_timestamp)
),

seller_details AS (
    SELECT
        m.seller_id,
        s.seller_state,
        m.sales_month,
        m.total_orders,
        m.item_sales,
        m.freight_cost
    FROM monthly_seller_sales AS m
    LEFT JOIN sellers AS s
        ON m.seller_id = s.seller_id
),

seller_trends AS (
    SELECT
        *,
        RANK() OVER (
            PARTITION BY sales_month
            ORDER BY item_sales DESC
        ) AS monthly_sales_rank,

        LAG(item_sales) OVER (
            PARTITION BY seller_id
            ORDER BY sales_month
        ) AS previous_month_sales,

        LAG(total_orders) OVER (
            PARTITION BY seller_id
            ORDER BY sales_month
        ) AS previous_month_orders

    FROM seller_details
)

SELECT
    seller_id,
    seller_state,
    sales_month,
    total_orders,
    ROUND(item_sales, 2) AS item_sales,
    ROUND(freight_cost, 2) AS freight_cost,
    ROUND(
        100.0 * freight_cost / NULLIF(item_sales, 0),
        2
    ) AS freight_pct_of_sales,
    monthly_sales_rank,
    ROUND(previous_month_sales, 2) AS previous_month_sales,

    CASE
        WHEN previous_month_sales IS NULL
            THEN 'No prior month'
        WHEN item_sales > previous_month_sales
            THEN 'Sales increased'
        WHEN item_sales < previous_month_sales
            THEN 'Sales decreased'
        ELSE 'Sales unchanged'
    END AS sales_trend

FROM seller_trends
ORDER BY sales_month DESC, monthly_sales_rank ASC;
