# SQL Scripts: Database Methodology

**Project:** Supply Chain Resiliency & Margin Protection in Prestige Beauty  
**Domain:** Prestige Beauty & Luxury CPG Supply Chain Analytics  
**Author:** Shari Nishida | Managing Director, NexGen Consulting, LLC  
**Dialect:** Standard ANSI SQL (compatible with SQLite, PostgreSQL, MySQL)

---

## Overview

The SQL pipeline handles three primary tasks: data normalization and schema standardization, feature engineering including the Tariff Impact Coefficient, and analytical view creation for downstream visualization in Tableau.

---

## File

| File | Description |
|---|---|
| `supply_chain_analysis.sql` | Full pipeline covering schema creation, feature engineering, analytical views, and cross-dataset bridge query |

---

## Database Design Decisions

### 1. Snake_Case Standardization

The raw Kaggle dataset uses mixed-case column names with spaces, which are incompatible with most SQL environments without quoting. The first step renames all columns to snake_case:

```sql
"Lead times"  →  supplier_lead_time
"Lead time"   →  delivery_lead_time
"Costs"       →  total_landed_cost
```

This matters analytically, not just stylistically. The two lead time fields, `supplier_lead_time` (days from PO to vendor dispatch) and `delivery_lead_time` (total order-to-delivery days), represent different stages of the supply chain. Disambiguating them in the schema makes the 9.9-day average planning variance visible and measurable.

---

### 2. Tariff Impact Coefficient: CASE WHEN Logic

The primary dataset restricts geographic metadata to five anonymized domestic manufacturing hubs, preventing a direct join with international tariff schedules. To model 2026 trade conditions without fabricating data, a Structural Attribute Proxy Strategy maps tariff penalties to `product_type` rather than location:

```sql
tariff_impact_coefficient = CASE
    WHEN LOWER(product_type) = 'cosmetics' THEN 0.25   -- Section 301 East Asia
    WHEN LOWER(product_type) = 'skincare'  THEN 0.10   -- EU MFN HS Chapter 33
    WHEN LOWER(product_type) = 'haircare'  THEN 0.00   -- Near-shore baseline
    ELSE NULL
END
```

**Why this is valid:** Cosmetics in this dataset are concentrated in secondary packaging and color cosmetics components, consistent with East Asian supply chains subject to Section 301 tariffs. Skincare actives and luxury glass packaging are consistent with European sourcing subject to EU MFN rates. Haircare is the control group representing near-shore or domestic supply.

**Tariff sources:**
- USTR Section 301: https://ustr.gov/issue-areas/enforcement/section-301-investigations/section-301-china/tariff-actions
- EU Commission HS Chapter 33: https://taxation-customs.ec.europa.eu/customs-4/calculation-customs-duties/customs-tariff_en

---

### 3. Engineered Features

Five calculated fields extend the cleaned table:

| Field | Formula | Purpose |
|---|---|---|
| `tariff_adjusted_mfg_cost` | `mfg_cost × (1 + tariff_coeff)` | COGS under current tariff conditions |
| `lead_time_variance` | `ABS(supplier_lt - delivery_lt)` | Planning buffer risk per SKU |
| `revenue_per_unit` | `revenue / units_sold` | Unit yield analysis |
| `stock_to_sales_ratio` | `stock_levels / units_sold` | Inventory health proxy |
| `gross_margin_baseline_pct` | `(revenue - mfg - shipping) / revenue × 100` | Pre-tariff gross margin |
| `gross_margin_tariff_pct` | `(revenue - tariff_mfg - shipping) / revenue × 100` | Post-tariff gross margin |
| `margin_compression_pp` | `baseline_pct - tariff_pct` | Percentage point compression |

---

### 4. Analytical Views

Six views are created, each corresponding to an EDA analysis:

| View | Maps To |
|---|---|
| `v_lead_time_variance` | Analysis #1: Lead Time Variance Distribution |
| `v_tariff_margin_analysis` | Analysis #4: Tariff-Adjusted Gross Margin |
| `v_defect_analysis` | Analysis #2: Defect Rate by Product Type |
| `v_inspection_by_supplier` | Analysis #3: Inspection Results by Supplier |
| `v_transport_analysis` | Analysis #5: Transportation Mode Trade-Off |
| `v_stockout_risk` | Analysis #6: Stockout Risk Mapping |

Views are designed to feed directly into Tableau and Power BI data connections without requiring additional transformation.

---

### 5. Category Bridge: Cross-Dataset Integration

The two datasets do not share a join key. A lightweight bridge table maps `product_type` (Dataset 1) to `primary_category` (Dataset 2) at the category level:

```sql
skincare   →  Skincare  (2,420 Sephora products, avg rating 4.31)
cosmetics  →  Makeup    (2,369 Sephora products, avg rating 4.19)
haircare   →  Hair      (1,464 Sephora products, avg rating 4.10)
```

The cross-dataset summary query joins supply chain risk metrics with Sephora demand signal metrics at the category level, enabling the S&OP integration hypothesis to be tested and validated.

---

## How to Run

```bash
# SQLite
sqlite3 prestige_beauty.db < supply_chain_analysis.sql

# PostgreSQL
psql -d prestige_beauty -f supply_chain_analysis.sql

# MySQL
mysql prestige_beauty < supply_chain_analysis.sql
```

---

## Enterprise Integration Note

The view outputs are structured to map directly to enterprise system parameters:

- `v_tariff_margin_analysis` → SAP S/4HANA Costing View inputs
- `v_stockout_risk` → Manhattan Active WMS Reorder Point (ROP) parameters
- `v_lead_time_variance` + `v_inspection_by_supplier` → Anaplan/o9 Solutions S&OP planning parameters

---

## Potential Future Enhancements

- A tariff sensitivity stress-test query modeling the gross margin impact of a hypothetical increase in EU skincare tariffs, the SQL equivalent of a dynamic what-if scenario tool, as a set-based query rather than a live dashboard control
