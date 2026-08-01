# Supply Chain Resiliency & Margin Protection in Prestige Beauty
### An Enterprise Systems Integration Case Study

**Author:** Shari Nishida  
**Industry Focus:** Prestige Beauty — Luxury CPG Supply Chain Analytics

---


How can a prestige beauty brand transition from a vulnerable, single-factory sourcing matrix to a resilient, multi-supplier network without diluting its retail gross margins?

This project builds an integrated scenario-modeling framework connecting supplier quality risk, tariff-driven cost exposure, and consumer demand signals. Each finding is then mapped to the enterprise system (ERP, WMS, or S&OP tooling) a real organization would use to act on it.

**Scope note:** the primary operational dataset contains 100 SKUs. This analysis is intentionally directional. It demonstrates methodology and relative risk ranking, not a statistically generalizable forecast.

## Datasets

| Dataset | Source | Details |
|---|---|---|
| Supply Chain Analysis Dataset | [Kaggle](https://www.kaggle.com/datasets/harshsingh2209/supply-chain-analysis) | 100 rows, 24 columns, 20.6 KB |
| Sephora Products and Skincare Reviews: Catalog | [Kaggle](https://www.kaggle.com/datasets/nadyinky/sephora-products-and-skincare-reviews) | `product_info.csv`, 8,494 rows, 27 columns |
| Sephora Products and Skincare Reviews: Reviews | Same source above | `reviews_0-250.csv` through `reviews_1250-end.csv`, 1,094,411 rows combined |

> **Note:** The five review files combined total 496.9 MB and exceed GitHub's 100 MB per-file limit. Do not commit these files to the repository. Download them directly from Kaggle and place them in the project root directory locally. `supply_chain_data.csv` (20.6 KB) and `product_info.csv` (7.5 MB) are both small enough to commit directly if you want the repo to run without a separate Kaggle download.

> **Data limitation (discovered during dashboard build):** every `product_id` in the reviews files maps exclusively to the Skincare category. There is zero overlap with Makeup or Hair. All review-based findings in this project (review velocity, price-tier growth) are therefore skincare-scoped, not portfolio-wide. This is disclosed on the datafolio, the dashboard, and in the final report.

## Key Findings

- **Supplier 4 carries a 66.7% inspection failure rate.** This is the single largest quality-concentration risk in the portfolio and the top priority for dual-sourcing.
- **Quality risk and tariff risk are independent dimensions.** Haircare has zero tariff exposure but the highest defect rate (2.48%) of any category.
- **Skincare is the highest-priority category for resilience investment.** It has the lowest stock-to-sales ratio (0.13), the most stockout-risk SKUs, the highest Sephora rating (4.31), and a 10% tariff premium.
- **Consumer review velocity is a validated leading demand signal**, within its skincare-only scope. Review volume grew 6.5x between 2015 and 2020.
- **Near-shoring can reduce both cost and lead time simultaneously** in this portfolio. Sea routes are both the cheapest and fastest transportation mode observed.

## Technical Stack

- **Python** (pandas, numpy, matplotlib, scipy), used for data profiling, cleaning, and EDA
- **SQL**, used for the relational schema and the category-based tariff proxy logic
- **Tableau Public**, used to build the three-tab interactive dashboard

## Live Dashboard

[Tableau Public: Supply Chain Resiliency & Margin Protection](https://public.tableau.com/app/profile/shari.nishida/viz/CorrelationOneDataAnalyticsCapstone/ExecutiveSOPRiskMatrix?publish=yes)

Three tabs, each scoped to a specific enterprise stakeholder:
1. **Executive S&OP Risk Matrix** (Supply Chain Director view)
2. **Margin Compression & Simulation** (CFO view)
3. **Omnichannel Inventory & WMS Calibration** (Warehouse Operations view)

## Repository Structure

```
prestige-beauty-supply-chain/
├── README.md
├── requirements.txt
├── .gitignore
├── docs/
│   ├── Project_Description_Shari_Nishida.pdf
│   ├── Project_Scope_Shari_Nishida.pdf
│   ├── Data_Curation_Shari_Nishida.pdf
│   ├── EDA_Shari_Nishida.pdf
│   ├── Datafolio_Shari_Nishida.pdf
│   ├── Dashboard_Submission_Shari_Nishida.pdf
│   └── Final_Report_Shari_Nishida.pdf
├── notebooks/
│   ├── README.md
│   └── eda_analysis.py
├── sql_scripts/
│   ├── README.md
│   └── supply_chain_analysis.sql
└── dashboards/
    ├── wireframe_eda_colors.svg
    ├── wireframe_eda_colors.png
    └── eda_charts/
        ├── chart1_defect_rate.png
        ├── chart2_margin.png
        ├── chart3_lead_time_variance.png
        ├── chart4_transport.png
        ├── chart5_inspection.png
        ├── chart6_review_velocity.png
        ├── chart7_exclusivity_rating.png
        └── chart8_stock_scatter.png
```

## Deliverable Status

| Deliverable | Status |
|---|---|
| Project Description & Scoping | ✅ Complete |
| Data Curation | ✅ Complete |
| Exploratory Data Analysis (EDA) | ✅ Complete |
| Datafolio | ✅ Complete |
| Dashboard (Tableau Public) | ✅ Complete (3 tabs live) |
| Final Report | ✅ Complete |

## How to Run

**Prerequisites:** Python 3.9+, `pip install -r requirements.txt`

**Dataset setup:**
1. Download `supply_chain_data.csv` from the Kaggle link above, or use the copy in this repo if included.
2. Download the Sephora `product_info.csv` and the five `reviews_*.csv` files from Kaggle. Place all files in the project root directory. Do **not** commit the review files to GitHub (see note above).

**Run the Python analysis:**
```
cd notebooks
python eda_analysis.py
```

**Run the SQL script** (example using SQLite):
```
sqlite3 supply_chain.db < sql_scripts/supply_chain_analysis.sql
```


---

## About the Author

Managing Director, NexGen Consulting, LLC. Specializing in business transformation, legacy system modernization, and data governance across Fortune 500 clients and government agencies. This project combines 20+ years of enterprise ERP configuration and supply chain consulting with modern cloud analytics to demonstrate how external data signals can drive real-time decision-making across global supply networks.

- **Core Strengths:** Strategy, Digital Transformation, ERP Integration, and Executive Advising
- **Certifications:** PMP, PMI-ACP, CSM, Oracle Cloud, AI
