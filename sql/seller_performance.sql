
SELECT
    oi.seller_id,
    COUNT(DISTINCT oi.order_id) AS total_orders,
    COUNT(*) AS total_items_sold,
    ROUND(SUM(oi.price), 2) AS total_sales,
    ROUND(SUM(oi.freight_value), 2) AS total_freight,
    ROUND(
        100.0 * SUM(oi.freight_value)
        / NULLIF(SUM(oi.price), 0),
        2
    ) AS freight_pct_of_sales
FROM order_items AS oi
GROUP BY oi.seller_id
HAVING SUM(oi.price) > 0
ORDER BY total_sales DESC
LIMIT 20;