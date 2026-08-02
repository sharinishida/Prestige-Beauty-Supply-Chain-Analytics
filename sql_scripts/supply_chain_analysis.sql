-- ============================================================
-- Supply Chain Resiliency & Margin Protection in Prestige Beauty
-- SQL Data Wrangling & Tariff Impact Coefficient Pipeline
-- Author: Shari Nishida  | Managing Director, NexGen Consulting, LLC    

-- ============================================================


-- ── STEP 1: CREATE CLEANED SUPPLY CHAIN TABLE ──────────────

CREATE TABLE supply_chain_cleaned AS
SELECT
    "Product type"          AS product_type,
    SKU                     AS sku,
    Price                   AS price,
    Availability            AS availability,
    "Number of products sold" AS units_sold,
    "Revenue generated"     AS revenue_generated,
    "Customer demographics" AS customer_demographics,
    "Stock levels"          AS stock_levels,
    "Order quantities"      AS order_quantities,
    "Shipping times"        AS shipping_times,
    "Shipping carriers"     AS shipping_carriers,
    "Shipping costs"        AS shipping_cost,
    "Supplier name"         AS supplier_name,
    Location                AS location,
    "Lead times"            AS supplier_lead_time,
    "Lead time"             AS delivery_lead_time,
    "Production volumes"    AS production_volumes,
    "Manufacturing lead time" AS manufacturing_lead_time,
    "Manufacturing costs"   AS manufacturing_cost,
    "Inspection results"    AS inspection_results,
    "Defect rates"          AS defect_rate,
    "Transportation modes"  AS transport_mode,
    Routes                  AS route,
    Costs                   AS total_landed_cost
FROM supply_chain_data;


-- ── STEP 2: TARIFF IMPACT COEFFICIENT ──────────────────────
-- Maps 2026 trade tariff penalties to product_type
-- Source: USTR Section 301 (East Asia) & EU MFN HS Chapter 33

ALTER TABLE supply_chain_cleaned
    ADD COLUMN tariff_impact_coefficient DECIMAL(5,2),
    ADD COLUMN tariff_tier               VARCHAR(20);

UPDATE supply_chain_cleaned
SET
    tariff_impact_coefficient = CASE
        WHEN LOWER(product_type) = 'cosmetics' THEN 0.25
        WHEN LOWER(product_type) = 'skincare'  THEN 0.10
        WHEN LOWER(product_type) = 'haircare'  THEN 0.00
        ELSE NULL
    END,
    tariff_tier = CASE
        WHEN LOWER(product_type) = 'cosmetics' THEN 'East Asia Section 301 (25%)'
        WHEN LOWER(product_type) = 'skincare'  THEN 'EU MFN Premium (10%)'
        WHEN LOWER(product_type) = 'haircare'  THEN 'Near-Shore Baseline (0%)'
        ELSE 'Unknown'
    END;


-- ── STEP 3: ENGINEERED FEATURES ────────────────────────────

ALTER TABLE supply_chain_cleaned
    ADD COLUMN tariff_adjusted_mfg_cost  DECIMAL(10,2),
    ADD COLUMN lead_time_variance        INTEGER,
    ADD COLUMN revenue_per_unit          DECIMAL(10,2),
    ADD COLUMN stock_to_sales_ratio      DECIMAL(10,4),
    ADD COLUMN gross_margin_baseline_pct DECIMAL(8,4),
    ADD COLUMN gross_margin_tariff_pct   DECIMAL(8,4),
    ADD COLUMN margin_compression_pp     DECIMAL(8,4);

UPDATE supply_chain_cleaned
SET
    tariff_adjusted_mfg_cost  = manufacturing_cost * (1 + tariff_impact_coefficient),
    lead_time_variance        = ABS(supplier_lead_time - delivery_lead_time),
    revenue_per_unit          = CASE WHEN units_sold > 0
                                     THEN revenue_generated / units_sold
                                     ELSE NULL END,
    stock_to_sales_ratio      = CASE WHEN units_sold > 0
                                     THEN stock_levels * 1.0 / units_sold
                                     ELSE NULL END,
    gross_margin_baseline_pct = CASE WHEN revenue_generated > 0
                                     THEN (revenue_generated - manufacturing_cost - shipping_cost)
                                          / revenue_generated * 100
                                     ELSE NULL END,
    gross_margin_tariff_pct   = CASE WHEN revenue_generated > 0
                                     THEN (revenue_generated
                                           - (manufacturing_cost * (1 + tariff_impact_coefficient))
                                           - shipping_cost)
                                          / revenue_generated * 100
                                     ELSE NULL END,
    margin_compression_pp     = gross_margin_baseline_pct - gross_margin_tariff_pct;


-- ── STEP 4: ANALYSIS VIEWS ─────────────────────────────────

-- Analysis #1: Lead Time Variance by Product Type
CREATE VIEW v_lead_time_variance AS
SELECT
    product_type,
    COUNT(*)                         AS sku_count,
    ROUND(AVG(supplier_lead_time),2) AS avg_supplier_lt,
    ROUND(AVG(delivery_lead_time),2) AS avg_delivery_lt,
    ROUND(AVG(lead_time_variance),2) AS avg_variance_days,
    MAX(lead_time_variance)          AS max_variance_days,
    SUM(CASE WHEN lead_time_variance > 20 THEN 1 ELSE 0 END)
                                     AS high_risk_sku_count
FROM supply_chain_cleaned
GROUP BY product_type
ORDER BY avg_variance_days DESC;


-- Analysis #2: Tariff Margin Compression by Product Type
CREATE VIEW v_tariff_margin_analysis AS
SELECT
    product_type,
    tariff_tier,
    tariff_impact_coefficient,
    ROUND(AVG(manufacturing_cost),2)     AS avg_baseline_mfg_cost,
    ROUND(AVG(tariff_adjusted_mfg_cost),2) AS avg_tariff_mfg_cost,
    ROUND(AVG(gross_margin_baseline_pct),4) AS avg_baseline_margin_pct,
    ROUND(AVG(gross_margin_tariff_pct),4)   AS avg_tariff_margin_pct,
    ROUND(AVG(margin_compression_pp),4)     AS avg_margin_compression_pp
FROM supply_chain_cleaned
GROUP BY product_type, tariff_tier, tariff_impact_coefficient
ORDER BY tariff_impact_coefficient DESC;


-- Analysis #3: Defect Rate by Product Type
CREATE VIEW v_defect_analysis AS
SELECT
    product_type,
    ROUND(AVG(defect_rate),3)                           AS avg_defect_rate,
    MIN(defect_rate)                                    AS min_defect_rate,
    MAX(defect_rate)                                    AS max_defect_rate,
    SUM(CASE WHEN defect_rate > 4.0 THEN 1 ELSE 0 END) AS high_defect_sku_count,
    COUNT(*)                                            AS total_skus
FROM supply_chain_cleaned
GROUP BY product_type
ORDER BY avg_defect_rate DESC;


-- Analysis #4: Inspection Results by Supplier
CREATE VIEW v_inspection_by_supplier AS
SELECT
    supplier_name,
    COUNT(*)                                                  AS total_skus,
    SUM(CASE WHEN inspection_results = 'Fail' THEN 1 ELSE 0 END)
                                                              AS fail_count,
    SUM(CASE WHEN inspection_results = 'Pass' THEN 1 ELSE 0 END)
                                                              AS pass_count,
    SUM(CASE WHEN inspection_results = 'Pending' THEN 1 ELSE 0 END)
                                                              AS pending_count,
    ROUND(
        SUM(CASE WHEN inspection_results = 'Fail' THEN 1 ELSE 0 END)
        * 100.0 / COUNT(*), 1
    )                                                         AS fail_rate_pct
FROM supply_chain_cleaned
GROUP BY supplier_name
ORDER BY fail_rate_pct DESC;


-- Analysis #5: Transportation Mode Cost vs Lead Time
CREATE VIEW v_transport_analysis AS
SELECT
    transport_mode,
    COUNT(*)                              AS sku_count,
    ROUND(AVG(shipping_cost),2)           AS avg_shipping_cost,
    ROUND(AVG(delivery_lead_time),2)      AS avg_delivery_lt,
    ROUND(AVG(supplier_lead_time),2)      AS avg_supplier_lt,
    ROUND(AVG(lead_time_variance),2)      AS avg_lt_variance
FROM supply_chain_cleaned
GROUP BY transport_mode
ORDER BY avg_shipping_cost DESC;


-- Analysis #6: Stockout Risk by Product Type
CREATE VIEW v_stockout_risk AS
SELECT
    product_type,
    COUNT(*)                                                       AS total_skus,
    ROUND(AVG(stock_levels),1)                                     AS avg_stock_level,
    ROUND(AVG(units_sold),1)                                       AS avg_units_sold,
    ROUND(AVG(stock_to_sales_ratio),4)                             AS avg_stock_to_sales,
    SUM(CASE WHEN stock_to_sales_ratio < 0.05 THEN 1 ELSE 0 END)  AS critical_stockout_risk_count
FROM supply_chain_cleaned
GROUP BY product_type
ORDER BY avg_stock_to_sales ASC;


-- ── STEP 5: TARIFF SENSITIVITY SCENARIO QUERY ──────────────
-- Dynamic scenario: what if EU tariff rises from 10% to 20%?
-- Replace @skincare_rate to model different scenarios

-- Standard scenario (current 2026 rates)
SELECT
    product_type,
    sku,
    manufacturing_cost                          AS baseline_mfg_cost,
    tariff_adjusted_mfg_cost                    AS current_tariff_mfg_cost,
    gross_margin_baseline_pct                   AS baseline_margin_pct,
    gross_margin_tariff_pct                     AS current_tariff_margin_pct,
    margin_compression_pp                       AS current_compression_pp,
    -- Stress test: EU skincare tariff doubles to 20%
    CASE
        WHEN LOWER(product_type) = 'skincare'
        THEN manufacturing_cost * 1.20
        ELSE tariff_adjusted_mfg_cost
    END                                         AS stress_test_mfg_cost,
    CASE
        WHEN LOWER(product_type) = 'skincare' AND revenue_generated > 0
        THEN (revenue_generated
              - (manufacturing_cost * 1.20)
              - shipping_cost)
             / revenue_generated * 100
        ELSE gross_margin_tariff_pct
    END                                         AS stress_test_margin_pct
FROM supply_chain_cleaned
ORDER BY product_type, margin_compression_pp DESC;


-- ── STEP 6: SEPHORA CATEGORY BRIDGE MAPPING ────────────────
-- Links Dataset 1 product_type to Dataset 2 primary_category

CREATE TABLE category_bridge (
    supply_chain_product_type VARCHAR(50),
    sephora_primary_category  VARCHAR(50),
    tariff_tier               VARCHAR(50)
);

INSERT INTO category_bridge VALUES
    ('skincare',  'Skincare', 'EU MFN Premium (10%)'),
    ('cosmetics', 'Makeup',   'East Asia Section 301 (25%)'),
    ('haircare',  'Hair',     'Near-Shore Baseline (0%)');

-- Cross-dataset summary query
SELECT
    b.supply_chain_product_type,
    b.sephora_primary_category,
    b.tariff_tier,
    sc.avg_defect_rate,
    sc.high_defect_sku_count,
    lt.avg_variance_days,
    lt.high_risk_sku_count,
    sr.avg_stock_to_sales,
    sr.critical_stockout_risk_count
FROM category_bridge b
LEFT JOIN v_defect_analysis  sc ON LOWER(b.supply_chain_product_type) = LOWER(sc.product_type)
LEFT JOIN v_lead_time_variance lt ON LOWER(b.supply_chain_product_type) = LOWER(lt.product_type)
LEFT JOIN v_stockout_risk sr ON LOWER(b.supply_chain_product_type) = LOWER(sr.product_type)
ORDER BY sr.avg_stock_to_sales ASC;
