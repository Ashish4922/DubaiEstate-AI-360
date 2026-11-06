# Dubai Property Transactions: Market Summary (DRAFT)

*Generated on 2026-11-06 from the project dataset. Draft for review. Learning prototype. Figures describe historical 2026 transactions only and are not investment advice.*

## 1. Dataset overview
- Rows loaded from both CSV parts: 134,185 [A1]
- Exact duplicate rows removed: 0 [A1]
- Transaction numbers that still appear more than once with different data (kept, not removed): 24 [A1]
- Rows removed as invalid (unparseable date or non-positive value): 0 [A1]
- Rows used in this report: 134,185 [A1]
- Date coverage: 2026-01-01 to 2026-10-29 [A1]

## 2. Sales activity by month
Sales transactions per calendar month [A2]:

| Month | Sales transactions |
|---|---|
| 2026-01 | 17,400 |
| 2026-02 | 17,015 |
| 2026-03 | 13,496 |
| 2026-04 | 14,011 |
| 2026-05 | 10,266 |
| 2026-06 | 13,927 |
| 2026-07 | 14,138 |
| 2026-08 | 11,813 |
| 2026-09 | 11,182 |
| 2026-10 (partial, data to 2026-10-29) | 10,937 |

Among complete months, 2026-01 had the most sales (17,400) and 2026-05 had the fewest (10,266) [A2].
The last month is incomplete, so it should not be compared with full months [A2].

## 3. Most active areas (top 5 by number of sales)
Total sales used: 134,185 [A3].

| Rank | Area | Sales transactions | Share of all sales |
|---|---|---|---|
| 1 | Madinat Al Mataar | 12,775 | 9.5% |
| 2 | JUMEIRAH VILLAGE CIRCLE | 8,602 | 6.4% |
| 3 | DUBAI LAND RESIDENCE COMPLEX | 5,219 | 3.9% |
| 4 | BUSINESS BAY | 5,152 | 3.8% |
| 5 | MAJAN | 4,424 | 3.3% |

Source for counts and shares: [A3].

## 4. Off-plan versus ready
Share of sales by status [A4]:

| Status | Sales transactions | Share |
|---|---|---|
| Off-Plan | 90,526 | 67.5% |
| Ready | 43,659 | 32.5% |

## 5. Median price per square metre (units only)
Across all unit-type sales, the median is AED 18,571 per sq m (sample 112,883) [A5]. Land and building sales are excluded because they are not comparable with individual units.

| Area | Median AED per sq m | Unit sales in sample | Note |
|---|---|---|---|
| Madinat Al Mataar [A6] | 18,354 | 11,931 |  |
| JUMEIRAH VILLAGE CIRCLE [A7] | 15,713 | 8,405 |  |
| DUBAI LAND RESIDENCE COMPLEX [A8] | 15,349 | 5,199 |  |
| BUSINESS BAY [A9] | 29,508 | 219 |  |
| MAJAN [A10] | 15,478 | 4,411 |  |

## 6. Example transactions
The largest recorded sale in each of the top 3 areas, so the figures above can be traced to real rows:

| Ref | Area | Transaction number | Date | Value (AED) | Area (sq m) |
|---|---|---|---|---|---|
| [R1] | Madinat Al Mataar | 41-6339-2026 | 2026-04-21 | 183,625,000 | 8,853.69 |
| [R2] | JUMEIRAH VILLAGE CIRCLE | 11-29379-2026 | 2026-09-25 | 188,270,919 | 12,144.84 |
| [R3] | DUBAI LAND RESIDENCE COMPLEX | 11-11039-2026 | 2026-03-14 | 127,500,000 | 6,011.29 |

## 7. Limitations
- The report describes past transactions only. It makes no statement about future prices.
- The dataset has no rent, occupancy, tenancy or maintenance fields, so none are discussed.
- Medians are used because a few very large sales would distort averages.
- Medians based on fewer than 30 rows are marked unreliable (a project convention, not a statistical rule).
- Some transaction numbers appear more than once with different data. Both rows were kept because the correct one cannot be determined from the file.
- Subtype labels are inconsistent in the source and some are blank, so this report groups by area and status rather than by subtype.
- Area names are used exactly as written in the source data.

## 8. Sources

| Ref | Source | Filters | Sample size | Date coverage |
|---|---|---|---|---|
| A1 | `retrieval.load_transactions()` | all rows in both CSV parts | 134,185 | 2026-01-01 to 2026-10-29 |
| A2 | `retrieval.monthly_sales_count(df)` | group=Sales | 134,185 | 2026-01-01 to 2026-10-29 |
| A3 | `retrieval.top_areas_by_count(df, 5)` | group=Sales | 134,185 | 2026-01-01 to 2026-10-29 |
| A4 | `retrieval.offplan_share(df)` | group=Sales | 134,185 | 2026-01-01 to 2026-10-29 |
| A5 | `retrieval.median_price_per_sqm(df)` | group=Sales; property_type=Unit; actual_area>0 | 112,883 | 2026-01-01 to 2026-10-29 |
| A6 | `retrieval.median_price_per_sqm(df, 'Madinat Al Mataar')` | group=Sales; property_type=Unit; actual_area>0; area=Madinat Al Mataar | 11,931 | 2026-01-01 to 2026-10-29 |
| A7 | `retrieval.median_price_per_sqm(df, 'JUMEIRAH VILLAGE CIRCLE')` | group=Sales; property_type=Unit; actual_area>0; area=JUMEIRAH VILLAGE CIRCLE | 8,405 | 2026-01-01 to 2026-10-29 |
| A8 | `retrieval.median_price_per_sqm(df, 'DUBAI LAND RESIDENCE COMPLEX')` | group=Sales; property_type=Unit; actual_area>0; area=DUBAI LAND RESIDENCE COMPLEX | 5,199 | 2026-01-01 to 2026-10-29 |
| A9 | `retrieval.median_price_per_sqm(df, 'BUSINESS BAY')` | group=Sales; property_type=Unit; actual_area>0; area=Business Bay | 219 | 2026-01-01 to 2026-10-29 |
| A10 | `retrieval.median_price_per_sqm(df, 'MAJAN')` | group=Sales; property_type=Unit; actual_area>0; area=MAJAN | 4,411 | 2026-01-01 to 2026-10-29 |
| R1 | `largest sale in area` | TRANSACTION_NUMBER=41-6339-2026; area=Madinat Al Mataar | 1 row | 2026-04-21 |
| R2 | `largest sale in area` | TRANSACTION_NUMBER=11-29379-2026; area=JUMEIRAH VILLAGE CIRCLE | 1 row | 2026-09-25 |
| R3 | `largest sale in area` | TRANSACTION_NUMBER=11-11039-2026; area=DUBAI LAND RESIDENCE COMPLEX | 1 row | 2026-03-14 |

*Learning prototype. Figures describe historical 2026 transactions only and are not investment advice.*
