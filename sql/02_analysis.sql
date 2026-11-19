-- ANALYSIS 1: Total financial loss due to shrinkage (spoilage) by product category
SELECT 
    p.category,
    SUM(s.shrinkage_units) AS total_shrinkage_units,
    ROUND(SUM(s.shrinkage_units * p.purchase_price), 2) AS financial_loss_eur,
    ROUND(SUM(s.units_sold * p.retail_price), 2) AS total_revenue_eur
FROM sales s
JOIN products p ON s.product_id = p.product_id
GROUP BY p.category
ORDER BY financial_loss_eur DESC;

-- ANALYSIS 2: Out-of-Stock (OOS) rate per store
SELECT 
    st.store_name,
    st.region,
    COUNT(*) AS checked_store_product_days,
    SUM(CASE WHEN i.current_stock = 0 THEN 1 ELSE 0 END) AS out_of_stock_events,
    ROUND(100.0 * SUM(CASE WHEN i.current_stock = 0 THEN 1 ELSE 0 END) / COUNT(*), 2) AS oos_rate_percent
FROM inventory i
JOIN stores st ON i.store_id = st.store_id
GROUP BY st.store_id, st.store_name, st.region
ORDER BY oos_rate_percent DESC;

-- ANALYSIS 3: Identify process bottlenecks (CTE) - Products with both high shrinkage AND frequent low stock
WITH product_kpis AS (
    SELECT 
        p.product_id,
        p.product_name,
        p.category,
        SUM(s.shrinkage_units) AS total_shrinkage,
        SUM(CASE WHEN i.current_stock < i.reorder_point THEN 1 ELSE 0 END) AS days_below_reorder_point
    FROM products p
    JOIN sales s ON p.product_id = s.product_id
    JOIN inventory i ON p.product_id = i.product_id 
        AND s.store_id = i.store_id 
        AND s.record_date = i.record_date
    GROUP BY p.product_id, p.product_name, p.category
)
SELECT 
    product_name,
    category,
    total_shrinkage,
    days_below_reorder_point,
    CASE 
        WHEN total_shrinkage > 150 AND days_below_reorder_point > 50 THEN 'Critical: Adjust order cycle'
        WHEN total_shrinkage > 150 THEN 'Reduce over-ordering'
        WHEN days_below_reorder_point > 50 THEN 'Increase reorder point'
        ELSE 'Process stable'
    END AS recommended_action
FROM product_kpis
ORDER BY total_shrinkage DESC;
