"""
EDA Analysis Script
Project: Supply Chain Resiliency & Margin Protection in Prestige Beauty
Author: Shari Nishida
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import warnings
warnings.filterwarnings('ignore')

# ── COLOR PALETTE ──
BLACK = '#000000'
SLATE = '#36454F'
LGREY = '#D8D0C4'
BGREY = '#F5F5F5'

# ── OUTPUT DIRECTORY ──
os.makedirs('eda_charts', exist_ok=True)

# ── LOAD SUPPLY CHAIN DATA ──
sc = pd.read_csv('supply_chain_data.csv')
sc.columns = [c.strip() for c in sc.columns]
sc = sc.rename(columns={
    'Lead times': 'supplier_lead_time',
    'Lead time': 'delivery_lead_time',
    'Costs': 'total_landed_cost',
    'Product type': 'product_type',
    'Number of products sold': 'units_sold',
    'Revenue generated': 'revenue',
    'Stock levels': 'stock_levels',
    'Manufacturing costs': 'mfg_cost',
    'Defect rates': 'defect_rate',
    'Shipping costs': 'shipping_cost',
    'Transportation modes': 'transport_mode',
    'Supplier name': 'supplier',
    'Inspection results': 'inspection'
})

# ── FEATURE ENGINEERING ──
tariff_map = {'cosmetics': 0.25, 'haircare': 0.00, 'skincare': 0.10}
sc['tariff_coeff'] = sc['product_type'].str.lower().map(tariff_map)
sc['tariff_adj_mfg'] = sc['mfg_cost'] * (1 + sc['tariff_coeff'])
sc['lead_time_variance'] = abs(sc['supplier_lead_time'] - sc['delivery_lead_time'])
sc['revenue_per_unit'] = sc['revenue'] / sc['units_sold']
sc['stock_to_sales'] = sc['stock_levels'] / sc['units_sold']
sc['gross_margin_baseline'] = (sc['revenue'] - sc['mfg_cost'] - sc['shipping_cost']) / sc['revenue'] * 100
sc['gross_margin_tariff'] = (sc['revenue'] - sc['tariff_adj_mfg'] - sc['shipping_cost']) / sc['revenue'] * 100
sc['margin_compression'] = sc['gross_margin_baseline'] - sc['gross_margin_tariff']

# ── LOAD SEPHORA DATA ──
prod = pd.read_csv('product_info.csv')
rev = pd.read_csv('reviews_0-250.csv')
rev['submission_time'] = pd.to_datetime(rev['submission_time'], errors='coerce')
rev['year'] = rev['submission_time'].dt.year
rev['month'] = rev['submission_time'].dt.month

# ── PRINT KEY STATISTICS ──
print("=== SUPPLY CHAIN KEY STATISTICS ===")
print(f"Records: {len(sc)} SKUs")
print(f"Lead time variance: avg={sc['lead_time_variance'].mean():.1f}d, max={sc['lead_time_variance'].max():.0f}d")
print(f"Defect rate: avg={sc['defect_rate'].mean():.2f}, max={sc['defect_rate'].max():.2f}")
print(f"Inspection fail rate: {(sc['inspection']=='Fail').mean()*100:.1f}%")
print(f"Baseline gross margin avg: {sc['gross_margin_baseline'].mean():.2f}%")
print(f"Tariff-adjusted margin avg: {sc['gross_margin_tariff'].mean():.2f}%")
print()
print("=== DEFECT RATE BY PRODUCT TYPE ===")
print(sc.groupby('product_type')['defect_rate'].mean().round(2))
print()
print("=== INSPECTION FAIL RATE BY SUPPLIER ===")
print(sc.groupby('supplier')['inspection'].apply(
    lambda x: f"{(x=='Fail').sum()/len(x)*100:.1f}%"
))
print()
print("=== TARIFF MARGIN COMPRESSION ===")
print(sc.groupby('product_type')['margin_compression'].mean().round(3))


# ── CHART 1: Defect Rate by Product Type ──
fig, ax = plt.subplots(figsize=(8, 5), facecolor='white')
means = sc.groupby('product_type')['defect_rate'].mean().sort_values(ascending=False)
bars = ax.bar(means.index, means.values, color=[BLACK, SLATE, LGREY], width=0.5, zorder=3)
ax.set_facecolor('white')
ax.grid(axis='y', color=LGREY, linewidth=0.5, zorder=0)
ax.set_xlabel('Product Type', fontsize=11, color=SLATE, labelpad=8)
ax.set_ylabel('Average Defect Rate (%)', fontsize=11, color=SLATE, labelpad=8)
ax.set_title('Average Defect Rate by Product Type', fontsize=13, fontweight='bold', color=BLACK, pad=14)
for bar, val in zip(bars, means.values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.03,
            f'{val:.2f}%', ha='center', va='bottom', fontsize=10, color=BLACK)
for spine in ax.spines.values(): spine.set_color(LGREY)
plt.tight_layout()
plt.savefig('eda_charts/chart1_defect_rate.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print("Chart 1 saved: eda_charts/chart1_defect_rate.png")


# ── CHART 2: Baseline vs Tariff-Adjusted Margin ──
fig, ax = plt.subplots(figsize=(9, 5), facecolor='white')
cats = ['cosmetics', 'haircare', 'skincare']
x = np.arange(len(cats))
w = 0.35
base = [sc[sc['product_type']==c]['gross_margin_baseline'].mean() for c in cats]
tariff = [sc[sc['product_type']==c]['gross_margin_tariff'].mean() for c in cats]
ax.bar(x - w/2, base, w, label='Baseline Margin', color=SLATE, zorder=3)
ax.bar(x + w/2, tariff, w, label='Tariff-Adjusted Margin', color=LGREY, zorder=3)
ax.set_facecolor('white')
ax.grid(axis='y', color=LGREY, linewidth=0.5, zorder=0)
ax.set_xticks(x)
ax.set_xticklabels([c.title() for c in cats], fontsize=11, color=SLATE)
ax.set_ylabel('Gross Margin (%)', fontsize=11, color=SLATE, labelpad=8)
ax.set_title('Baseline vs. Tariff-Adjusted Gross Margin by Product Type',
             fontsize=13, fontweight='bold', color=BLACK, pad=14)
ax.set_ylim(97.5, 99.5)
ax.legend(fontsize=10)
for spine in ax.spines.values(): spine.set_color(LGREY)
plt.tight_layout()
plt.savefig('eda_charts/chart2_margin.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print("Chart 2 saved: eda_charts/chart2_margin.png")


# ── CHART 3: Lead Time Variance Histogram ──
fig, ax = plt.subplots(figsize=(8, 5), facecolor='white')
ax.hist(sc['lead_time_variance'], bins=14, color=SLATE, edgecolor='white', zorder=3, alpha=0.85)
ax.axvline(sc['lead_time_variance'].mean(), color=BLACK, linestyle='--', linewidth=1.5,
           label=f"Mean: {sc['lead_time_variance'].mean():.1f} days")
ax.set_facecolor('white')
ax.grid(axis='y', color=LGREY, linewidth=0.5, zorder=0)
ax.set_xlabel('Lead Time Variance (days)', fontsize=11, color=SLATE, labelpad=8)
ax.set_ylabel('Number of SKUs', fontsize=11, color=SLATE, labelpad=8)
ax.set_title('Distribution of Lead Time Variance Across 100 SKUs',
             fontsize=13, fontweight='bold', color=BLACK, pad=14)
ax.legend(fontsize=10)
for spine in ax.spines.values(): spine.set_color(LGREY)
plt.tight_layout()
plt.savefig('eda_charts/chart3_lead_time_variance.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print("Chart 3 saved: eda_charts/chart3_lead_time_variance.png")


# ── CHART 4: Transportation Mode Cost vs Lead Time ──
fig, ax1 = plt.subplots(figsize=(9, 5), facecolor='white')
modes = sc.groupby('transport_mode')[['shipping_cost','delivery_lead_time']].mean().sort_values(
    'shipping_cost', ascending=False)
x = np.arange(len(modes))
ax1.bar(x, modes['shipping_cost'], color=BLACK, width=0.4, label='Avg Shipping Cost ($)', zorder=3)
ax1.set_ylabel('Avg Shipping Cost ($)', fontsize=11, color=BLACK, labelpad=8)
ax2 = ax1.twinx()
ax2.plot(x, modes['delivery_lead_time'], color=LGREY, marker='o', linewidth=2.5,
         markersize=8, label='Avg Delivery Lead Time (days)')
ax2.set_ylabel('Avg Delivery Lead Time (days)', fontsize=11, color=SLATE, labelpad=8)
ax1.set_xticks(x)
ax1.set_xticklabels(modes.index, fontsize=11, color=SLATE)
ax1.set_facecolor('white')
ax1.grid(axis='y', color=LGREY, linewidth=0.5, zorder=0)
ax1.set_title('Transportation Mode: Shipping Cost vs. Delivery Lead Time',
              fontsize=13, fontweight='bold', color=BLACK, pad=14)
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1+lines2, labels1+labels2, fontsize=9)
for spine in ax1.spines.values(): spine.set_color(LGREY)
plt.tight_layout()
plt.savefig('eda_charts/chart4_transport.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print("Chart 4 saved: eda_charts/chart4_transport.png")


# ── CHART 5: Inspection Results by Supplier ──
fig, ax = plt.subplots(figsize=(10, 5), facecolor='white')
insp = pd.crosstab(sc['supplier'], sc['inspection'])
insp[['Fail','Pass','Pending']].plot(
    kind='bar', ax=ax, color=[BLACK, LGREY, SLATE], width=0.6, zorder=3, edgecolor='white')
ax.set_facecolor('white')
ax.grid(axis='y', color=LGREY, linewidth=0.5, zorder=0)
ax.set_xlabel('Supplier', fontsize=11, color=SLATE, labelpad=8)
ax.set_ylabel('Number of SKUs', fontsize=11, color=SLATE, labelpad=8)
ax.set_title('Inspection Results by Supplier: Defect Concentration Analysis',
             fontsize=13, fontweight='bold', color=BLACK, pad=14)
ax.tick_params(axis='x', rotation=0)
ax.legend(['Fail', 'Pass', 'Pending'], fontsize=10)
for spine in ax.spines.values(): spine.set_color(LGREY)
plt.tight_layout()
plt.savefig('eda_charts/chart5_inspection.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print("Chart 5 saved: eda_charts/chart5_inspection.png")


# ── CHART 6: Sephora Review Velocity by Year ──
yearly = rev.groupby('year').size().reset_index(name='review_count')
yearly = yearly[yearly['year'] >= 2010]
fig, ax = plt.subplots(figsize=(10, 5), facecolor='white')
ax.fill_between(yearly['year'], yearly['review_count'], alpha=0.15, color=SLATE)
ax.plot(yearly['year'], yearly['review_count'], color=BLACK, linewidth=2.5, marker='o', markersize=6)
ax.set_facecolor('white')
ax.grid(axis='y', color=LGREY, linewidth=0.5)
ax.set_xlabel('Year', fontsize=11, color=SLATE, labelpad=8)
ax.set_ylabel('Review Volume', fontsize=11, color=SLATE, labelpad=8)
ax.set_title('Sephora Consumer Review Velocity 2010 to 2023\n(Leading Demand Signal for S&OP Planning)',
             fontsize=13, fontweight='bold', color=BLACK, pad=14)
ax.axvline(2020, color=LGREY, linestyle=':', linewidth=1.5)
ax.text(2020.1, yearly['review_count'].max()*0.85, 'COVID-19\nPeak 2020', fontsize=9, color=SLATE)
for spine in ax.spines.values(): spine.set_color(LGREY)
plt.tight_layout()
plt.savefig('eda_charts/chart6_review_velocity.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print("Chart 6 saved: eda_charts/chart6_review_velocity.png")


# ── CHART 7: Rating by Exclusivity Tier ──
prod_r = prod[prod['rating'].notna()]
fig, axes = plt.subplots(1, 2, figsize=(11, 5), facecolor='white')
le_data = [prod_r[prod_r['limited_edition']==0]['rating'].values,
           prod_r[prod_r['limited_edition']==1]['rating'].values]
bp1 = axes[0].boxplot(le_data, patch_artist=True, labels=['Standard', 'Limited Edition'],
                       medianprops=dict(color=BLACK, linewidth=2))
bp1['boxes'][0].set_facecolor(LGREY)
bp1['boxes'][1].set_facecolor(SLATE)
axes[0].set_title('Rating: Limited Edition vs. Standard', fontsize=12, fontweight='bold', color=BLACK)
axes[0].set_ylabel('Rating', fontsize=10, color=SLATE)
axes[0].set_facecolor('white')
axes[0].grid(axis='y', color=LGREY, linewidth=0.5)
se_data = [prod_r[prod_r['sephora_exclusive']==0]['rating'].values,
           prod_r[prod_r['sephora_exclusive']==1]['rating'].values]
bp2 = axes[1].boxplot(se_data, patch_artist=True, labels=['Multi-Retailer', 'Sephora Exclusive'],
                       medianprops=dict(color=BLACK, linewidth=2))
bp2['boxes'][0].set_facecolor(LGREY)
bp2['boxes'][1].set_facecolor(SLATE)
axes[1].set_title('Rating: Sephora Exclusive vs. Multi-Retailer', fontsize=12, fontweight='bold', color=BLACK)
axes[1].set_ylabel('Rating', fontsize=10, color=SLATE)
axes[1].set_facecolor('white')
axes[1].grid(axis='y', color=LGREY, linewidth=0.5)
for ax in axes:
    for spine in ax.spines.values(): spine.set_color(LGREY)
fig.suptitle('Consumer Rating Distribution by Product Exclusivity Tier',
             fontsize=13, fontweight='bold', color=BLACK)
plt.tight_layout()
plt.savefig('eda_charts/chart7_exclusivity_rating.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print("Chart 7 saved: eda_charts/chart7_exclusivity_rating.png")


# ── CHART 8: Stock Levels vs Units Sold Scatter ──
fig, ax = plt.subplots(figsize=(8, 5), facecolor='white')
colors_map = {'cosmetics': BLACK, 'haircare': SLATE, 'skincare': LGREY}
for pt, group in sc.groupby('product_type'):
    ax.scatter(group['units_sold'], group['stock_levels'],
               color=colors_map[pt], label=pt.title(), alpha=0.7, s=60, zorder=3)
ax.set_facecolor('white')
ax.grid(color=LGREY, linewidth=0.5, zorder=0)
ax.set_xlabel('Units Sold', fontsize=11, color=SLATE, labelpad=8)
ax.set_ylabel('Stock Levels', fontsize=11, color=SLATE, labelpad=8)
ax.set_title('Stock Levels vs. Units Sold by Product Type: Stockout Risk Zones',
             fontsize=13, fontweight='bold', color=BLACK, pad=14)
ax.legend(fontsize=10)
ax.axhline(20, color=LGREY, linestyle='--', linewidth=1)
for spine in ax.spines.values(): spine.set_color(LGREY)
plt.tight_layout()
plt.savefig('eda_charts/chart8_stock_scatter.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print("Chart 8 saved: eda_charts/chart8_stock_scatter.png")

print("\nAll 8 charts generated successfully.")
