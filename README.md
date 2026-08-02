# Supply Chain Resiliency & Margin Protection in Prestige Beauty
### An Enterprise Systems Integration Case Study

**Project:** Supply Chain Resiliency & Margin Protection in Prestige Beauty  
**Domain:** Prestige Beauty & Luxury CPG Supply Chain Analytics  
**Author:** Shari Nishida | Managing Director, NexGen Consulting, LLC    
**Primary Assets:** [Executive Notion Hub](https://shari-nishida.notion.site) | [Tableau Public Dashboard](https://public.tableau.com/app/profile/shari.nishida/viz/CorrelationOneDataAnalyticsCapstone/ExecutiveSOPRiskMatrix?publish=yes)

---

## Executive Overview

How can a prestige beauty brand transition from a vulnerable, single-factory sourcing matrix to a resilient, multi-supplier network without diluting its retail gross margins?

This project delivers an integrated scenario-modeling framework connecting supplier quality risk, tariff-driven cost exposure, and consumer demand signals. Each finding is directly mapped to the enterprise systems, ERP (SAP), WMS (Manhattan Active), and S&OP tooling (Anaplan), required to execute operational change.

**Scope Note:** The primary operational dataset contains a baseline of 100 SKUs. This analysis is intentionally directional, built to demonstrate enterprise methodology and relative risk ranking rather than a statistically generalizable macro forecast.

---

## Key Business Insights

* **Supplier 4 represents the primary quality failure point.** It carries a **66.7% inspection failure rate** (12 of 18 SKUs), the single largest quality-concentration risk in the portfolio and the top priority for dual-sourcing intervention.
* **Quality risk and tariff risk operate independently.** Haircare maintains zero tariff exposure under current trade schedules but exhibits the highest defect rate (2.48%) across all categories.
* **Skincare is the highest-priority category for resilience investment.** It carries the lowest stock-to-sales ratio (0.13), the highest concentration of stockout-risk SKUs, the highest Sephora consumer rating (4.31), and a 10% tariff premium.
* **Consumer review velocity serves as a validated leading demand signal.** Within its skincare-only scope, review volume expanded 6.5x between 2015 and 2020, serving as an early-warning indicator for safety stock adjustments.
* **Transportation mode optimization.** Sea freight proves to be both the most cost-effective and fastest shipping mode observed within this portfolio structure.

---

## Enterprise Technical Stack

* **Python 3.9+** (`pandas`, `numpy`, `matplotlib`, `scipy`): data profiling, feature engineering, and exploratory data analysis
* **SQL**: relational schema design and category-based tariff proxy logic
* **Tableau Public**: interactive multi-tab enterprise decision dashboard

---

## Interactive Decision Tool

The live dashboard is structured across three dedicated tabs, each aligned to a key enterprise decision-maker:

| Dashboard View | Primary Persona | Key Functional Metrics |
| :--- | :--- | :--- |
| **1. Executive S&OP Risk Matrix** | Supply Chain Director | Defect rates, lead-time variability, and cost vs. revenue by SKU |
| **2. Margin Compression & Simulation** | Chief Financial Officer (CFO) | Tariff-adjusted margin waterfall and live near-shore cost simulator |
| **3. Omnichannel Inventory & WMS** | Warehouse Operations | Reorder-point calibration tables and stockout risk matrices |

**Live Dashboard:** [View Workbook on Tableau Public](https://public.tableau.com/app/profile/shari.nishida/viz/CorrelationOneDataAnalyticsCapstone/ExecutiveSOPRiskMatrix?publish=yes)

---

## Data Architecture & Scoping Disclosures

| Dataset | Source | Schema & Scale | Repo Status |
| :--- | :--- | :--- | :--- |
| **Supply Chain Analysis** | [Kaggle](https://www.kaggle.com/datasets/harshsingh2209/supply-chain-analysis) | 100 rows, 24 columns (20.6 KB) | Committed |
| **Sephora Catalog** | [Kaggle](https://www.kaggle.com/datasets/nadyinky/sephora-products-and-skincare-reviews) | `product_info.csv` (8,494 rows, 27 columns) | Committed |
| **Sephora Reviews** | Same as above | 5 split CSV files (1,094,411 rows combined, 496.9 MB) | External (excluded via `.gitignore`) |

> **Data Limitation Disclosures**
> 1. **Repository limits:** GitHub's 100 MB per-file constraint excludes the 496.9 MB Sephora review files from git tracking. Local ingestion instructions are provided below.
> 2. **Category scope:** A data audit confirmed that every `product_id` within the Sephora review files maps exclusively to **Skincare**. Sentiment and review-velocity findings apply strictly to Skincare and are not extrapolated across Makeup or Haircare.

---

## Repository Structure

```text
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

---

## Project Status

| Project Phase | Status |
| :--- | :--- |
| **Project Description & Scoping** | Complete |
| **Data Curation & Feature Engineering** | Complete |
| **Exploratory Data Analysis (EDA)** | Complete |
| **Executive Datafolio** | Complete |
| **Interactive Tableau Dashboard** | Complete, 3 tabs live |
| **Final Technical Report** | Complete |

---

## Execution Guide

### 1. Environment Prerequisites
* Python 3.9+
* Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```

### 2. Data Ingestion
1. Ensure `supply_chain_data.csv` and `product_info.csv` are located in the project root.
2. Download the five Sephora review CSV files (`reviews_0-250.csv` through `reviews_1250-end.csv`) directly from Kaggle and place them in the root directory.

### 3. Pipeline Execution
Run the core Python exploratory analysis:
```bash
cd notebooks
python eda_analysis.py
```

Run the SQL schema and analytical scripts (e.g., using SQLite):
```bash
sqlite3 supply_chain.db < sql_scripts/supply_chain_analysis.sql
```

---

## About the Author

**Shari Nishida**
*Managing Director, NexGen Consulting, LLC*

Specializing in business transformation, legacy system modernization, and data governance across Fortune 500 enterprises and public sector agencies. This project bridges 20+ years of enterprise ERP configuration and supply chain advisory experience with modern cloud analytics, demonstrating how external data signals can drive real-time resilience across global supply networks.

* **Core Competencies:** Strategy, Digital Transformation, ERP Architecture (SAP/Oracle), Executive Advising
* **Credentials:** PMP, PMI-ACP, CSM, Oracle Cloud Certified, AI Specialist

---

## Generative AI Disclosure

Claude (Anthropic) was used throughout this project as a development, QA, and documentation partner, including dataset profiling execution, stress-testing the tariff proxy logic, identifying and resolving Tableau build issues, and reviewing drafts for consistency and clarity. All architectural decisions, domain interpretations, and analytical judgments reflect the author's own expertise and 20+ years of professional ERP and supply chain consulting experience.
