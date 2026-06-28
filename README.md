# 90-Day PLA Naval Blockade: Supply Chain Cascade Analysis

## Overview
Python-based scenario model and interactive dashboard quantifying US semiconductor supply chain disruption across 30, 60, and 90-day PLA naval blockade durations. Analysis covers cascade effects on DoD defense procurement contracts and medical device categories.

**[Live Dashboard](https://tylerbrown11141.github.io/taiwan-blockade-analysis/taiwan_blockade_dashboard.html)**

## Key Findings
- HTS 8542 (integrated circuits) carries 23.3% Taiwan import dependency — the dominant exposure category
- A 90-day blockade produces a 19.8% supply shock to integrated circuit imports
- Raytheon ($52.2B), Lockheed Martin ($29.8B), and Northrop Grumman ($27.4B) carry the highest Taiwan-exposed DoD contract values in NAICS 334511 (navigation/guidance systems)
- Implantable and imaging medical devices face critical shortage onset by day 69-72 of a 90-day blockade

## Methodology
- **Supply shock formula:** taiwan_import_share × disruption_rate × (1 − inventory_buffer_factor)
- **Disruption rates:** 30-day = 40%, 60-day = 65%, 90-day = 85%
- **Inventory buffer:** 60-90 day industry standard (SIA Factbook; chipmaker earnings calls)
- **Defense exposure score:** contract_value_usd × taiwan_dependency_pct

## Data Sources
| Dataset | Source |
|---|---|
| US semiconductor imports by country | US Census Bureau — usatrade.census.gov, HTS 8541-8543 |
| Semiconductor imports by end-use | USITC DataWeb — dataweb.usitc.gov |
| TSMC platform revenue breakdown | TSMC 2023 Annual Report — investor.tsmc.com |
| SIA Semiconductor Factbook | semiconductors.org/resources |
| DoD contract awards FY2024 | USASpending.gov — NAICS 334xx |
| Medical device supply chain disclosures | SEC EDGAR — Medtronic (MDT), Abbott (ABT) 10-K filings |

## Stack
Python 3.14 · pandas · Plotly · Jupyter

## Author
