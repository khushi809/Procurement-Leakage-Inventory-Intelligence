
WITH seller_sales AS (
    SELECT
        oi.seller_id,
        COUNT(DISTINCT oi.order_id) AS total_orders,
        ROUND(SUM(oi.price), 2) AS total_sales,
        ROUND(SUM(oi.freight_value), 2) AS total_freight,
        ROUND(
            100.0 * SUM(oi.freight_value)
            / NULLIF(SUM(oi.price), 0),
            2
        ) AS freight_to_sales_pct
    FROM order_items oi
    JOIN orders o
        ON oi.order_id = o.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY oi.seller_id
),

seller_order_delivery AS (
    SELECT DISTINCT
        oi.seller_id,
        o.order_id,
        o.order_delivered_customer_date,
        o.order_estimated_delivery_date
    FROM order_items oi
    JOIN orders o
        ON oi.order_id = o.order_id
    WHERE o.order_status = 'delivered'
      AND o.order_delivered_customer_date IS NOT NULL
      AND o.order_estimated_delivery_date IS NOT NULL
),

seller_delivery AS (
    SELECT
        seller_id,
        COUNT(*) AS eligible_delivery_orders,
        SUM(
            CASE
                WHEN order_delivered_customer_date
                     > order_estimated_delivery_date
                THEN 1 ELSE 0
            END
        ) AS late_orders,
        ROUND(
            100.0 * SUM(
                CASE
                    WHEN order_delivered_customer_date
                         > order_estimated_delivery_date
                    THEN 1 ELSE 0
                END
            ) / NULLIF(COUNT(*), 0),
            2
        ) AS late_delivery_pct
    FROM seller_order_delivery
    GROUP BY seller_id
),

seller_review_order AS (
    SELECT
        oi.seller_id,
        o.order_id,
        AVG(r.review_score) AS order_review_score
    FROM order_items oi
    JOIN orders o
        ON oi.order_id = o.order_id
    JOIN order_reviews r
        ON o.order_id = r.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY oi.seller_id, o.order_id
),

seller_reviews AS (
    SELECT
        seller_id,
        ROUND(AVG(order_review_score), 2) AS avg_review_score,
        COUNT(*) AS reviewed_orders
    FROM seller_review_order
    GROUP BY seller_id
),

seller_metrics AS (
    SELECT
        ss.seller_id,
        ss.total_orders,
        ss.total_sales,
        ss.total_freight,
        ss.freight_to_sales_pct,
        COALESCE(sd.eligible_delivery_orders, 0)
            AS eligible_delivery_orders,
        COALESCE(sd.late_orders, 0) AS late_orders,
        sd.late_delivery_pct,
        sr.avg_review_score,
        COALESCE(sr.reviewed_orders, 0) AS reviewed_orders
    FROM seller_sales ss
    LEFT JOIN seller_delivery sd
        ON ss.seller_id = sd.seller_id
    LEFT JOIN seller_reviews sr
        ON ss.seller_id = sr.seller_id
),

risk_flags AS (
    SELECT *,
        CASE
            WHEN freight_to_sales_pct >= 20 THEN 1 ELSE 0
        END AS high_freight_flag,
        CASE
            WHEN late_delivery_pct >= 15 THEN 1 ELSE 0
        END AS high_delay_flag,
        CASE
            WHEN avg_review_score < 3 THEN 1 ELSE 0
        END AS low_review_flag
    FROM seller_metrics
)

SELECT
    *,
    CASE
        WHEN total_orders < 10 THEN 'Low sample size'
        ELSE 'Sufficient for initial screening'
    END AS sample_size_status,
    high_freight_flag + high_delay_flag + low_review_flag
        AS risk_flag_count,
    CASE
        WHEN total_orders < 10 THEN 'Monitor - limited data'
        WHEN high_freight_flag + high_delay_flag + low_review_flag >= 2
            THEN 'High priority investigation'
        WHEN high_freight_flag + high_delay_flag + low_review_flag = 1
            THEN 'Review recommended'
        ELSE 'No major flags'
    END AS investigation_category,
    RANK() OVER (
        ORDER BY
            CASE WHEN total_orders < 10 THEN 1 ELSE 0 END,
            high_freight_flag + high_delay_flag + low_review_flag DESC,
            late_delivery_pct DESC,
            freight_to_sales_pct DESC
    ) AS investigation_rank
FROM risk_flags
ORDER BY investigation_rank, total_sales DESC;
