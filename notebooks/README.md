# Python Data Mining Pipeline

**Project:** Supply Chain Resiliency & Margin Protection in Prestige Beauty  
**Domain:** Prestige Beauty & Luxury CPG Supply Chain Analytics  
**Author:** Shari Nishida | Managing Director, NexGen Consulting, LLC  
**Libraries:** pandas, numpy, matplotlib, scipy

---

## Overview

The Python pipeline covers three stages: data profiling and quality assessment, feature engineering including the Tariff Impact Coefficient, and exploratory data analysis with chart generation. All numerical outputs are derived from actual data execution on the raw Kaggle datasets.

---

## File

| File | Description |
|---|---|
| `eda_analysis.py` | Full EDA pipeline covering data loading, feature engineering, statistical analysis, and 8 chart outputs |

---

## Pipeline Architecture

### Stage 1: Data Loading and Schema Normalization

The raw supply chain CSV uses mixed-case column names with spaces. The first pipeline step renames all columns to snake_case for compatibility with pandas operations and SQL schema alignment:

```python
sc = sc.rename(columns={
    'Lead times': 'supplier_lead_time',
    'Lead time':  'delivery_lead_time',
    'Costs':      'total_landed_cost',
    ...
})
```

The Sephora review files are loaded individually and parsed for time-series analysis. The `submission_time` field is cast to datetime and decomposed into `year` and `month` fields to enable review velocity trend analysis across 2008 to 2023.

---

### Stage 2: Feature Engineering

Five engineered variables extend the supply chain dataset. Each reflects a real enterprise analytics concept:

**Tariff Impact Coefficient**
Maps 2026 trade tariff penalties to product category using a dictionary lookup:

```python
tariff_map = {'cosmetics': 0.25, 'haircare': 0.00, 'skincare': 0.10}
sc['tariff_coeff'] = sc['product_type'].str.lower().map(tariff_map)
sc['tariff_adj_mfg'] = sc['mfg_cost'] * (1 + sc['tariff_coeff'])
```

This replicates the CASE WHEN logic in the SQL pipeline, implemented here as a vectorized pandas operation for performance across the full dataset.

**Lead Time Variance**
Quantifies planning buffer risk per SKU by measuring the gap between supplier dispatch lead time and total delivery lead time:

```python
sc['lead_time_variance'] = abs(sc['supplier_lead_time'] - sc['delivery_lead_time'])
```

Average variance of 9.9 days, maximum of 28 days across 100 SKUs.

**Gross Margin: Baseline and Tariff-Adjusted**
```python
sc['gross_margin_baseline'] = (sc['revenue'] - sc['mfg_cost'] - sc['shipping_cost']) / sc['revenue'] * 100
sc['gross_margin_tariff']   = (sc['revenue'] - sc['tariff_adj_mfg'] - sc['shipping_cost']) / sc['revenue'] * 100
sc['margin_compression']    = sc['gross_margin_baseline'] - sc['gross_margin_tariff']
```

**Stock-to-Sales Ratio**
```python
sc['stock_to_sales'] = sc['stock_levels'] / sc['units_sold']
```

SKUs below 0.05 are flagged as critical stockout risk zones.

---

### Stage 3: Exploratory Data Analysis

Eight analyses are executed, each generating a chart saved to the `eda_charts/` directory. All charts use a consistent three-color palette matching the project document styling:

```python
BLACK = '#000000'   # Primary bars, headings, solid lines
SLATE = '#36454F'   # Secondary bars, dashed lines, axis labels
LGREY = '#D8D0C4'   # Grid lines, borders, tertiary category
```

| Chart | File | Analysis |
|---|---|---|
| Defect Rate by Product Type | `chart1_defect_rate.png` | Bar chart showing average defect rate per category |
| Baseline vs. Tariff Margin | `chart2_margin.png` | Grouped bar showing margin compression by tariff tier |
| Lead Time Variance | `chart3_lead_time_variance.png` | Histogram showing distribution across 100 SKUs |
| Transport Mode Trade-Off | `chart4_transport.png` | Dual-axis bar and line chart showing cost vs. lead time |
| Inspection by Supplier | `chart5_inspection.png` | Stacked bar showing Pass/Fail/Pending by vendor |
| Review Velocity 2010 to 2023 | `chart6_review_velocity.png` | Area/line chart showing Sephora review volume trend |
| Rating by Exclusivity Tier | `chart7_exclusivity_rating.png` | Side-by-side box plots |
| Stock vs. Units Sold | `chart8_stock_scatter.png` | Scatter plot showing stockout risk zone mapping |

---

## Key Statistical Findings

All values derived from actual data execution:

| Metric | Value |
|---|---|
| Supply chain records | 100 SKUs, 24 fields |
| Average lead time variance | 9.9 days |
| Maximum lead time variance | 28 days |
| Average defect rate | 2.28% |
| Inspection failure rate | 36% |
| Supplier 4 failure rate | 66.7% |
| Sephora products analyzed | 8,494 |
| Total consumer reviews | 1,094,411 |
| Review date range | August 2008 to March 2023 |
| Peak review year | 2020 (125,824 reviews) |
| Review velocity growth 2015 to 2020 | 6.5x |

---

## Dataset Integration Methodology

The two datasets do not share a direct join key. A structural category bridge links them at the product category level:

```python
merged = rev.merge(
    prod[['product_id', 'primary_category', 'price_usd',
          'out_of_stock', 'limited_edition', 'sephora_exclusive']],
    on='product_id',
    how='left'
)
```

The Sephora `product_id` foreign key connects the product catalog to the reviews file. Supply chain `product_type` maps to Sephora `primary_category` via the bridge table documented in the SQL pipeline.

---

## How to Run

```bash
# Install dependencies
pip install -r requirements.txt

# Run full pipeline
python eda_analysis.py
```

Charts are saved to `eda_charts/`. Console output displays all key statistical findings.

---

## Potential Future Enhancements

- Jupyter Notebook version of `eda_analysis.py` with inline chart rendering
- scipy-based optimization model for dual-sourcing volume split scenarios
- Time-series decomposition of Sephora review velocity by category
- Safety stock and Reorder Point (ROP) parameter calculation notebook
