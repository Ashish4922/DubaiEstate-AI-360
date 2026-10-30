# Data Quality Validation Report – Dubai Real Estate Transactions

## 1. Dataset Overview

The analysis uses two source CSV files:

- dubai_transactions_2026_part_1.csv
- dubai_transactions_2026_part_2.csv

Both files contain 22 columns, and their headers match.

The original source CSV files were kept unchanged.

## 2. Record Count Validation

| Metric | Part 1 | Part 2 | Combined |
|---|---:|---:|---:|
| Total Records | 127,000 | 7,185 | 134,185 |
| Unique Transaction Numbers | 126,976 | 7,185 | 134,161 |
| Repeated Transaction Number Groups | 24 | 0 | 24 |
| Extra Occurrences | 24 | 0 | 24 |

No common transaction numbers were found across the two files.

## 3. Transaction Number Validation

### Part 1

- Total records: 127,000
- Unique transaction numbers: 126,976
- Repeated transaction-number groups: 24
- Each repeated transaction number occurs exactly twice.

All 24 repeated pairs were compared across all 22 columns.

### Findings

- 23 pairs differ in NEAREST_METRO_EN.
- 1 pair differs in NEAREST_MALL_EN.
- No pair is identical across all 22 columns.

These records are not exact duplicate rows. Repeated transaction numbers should not automatically be treated as duplicate transactions.

### Part 2

- Total records: 7,185
- Unique transaction numbers: 7,185
- Repeated transaction-number groups: 0

No repeated transaction numbers were found in Part 2.

## 4. Date Validation

- Valid date records: 134,185
- Earliest transaction date: 2026-01-01 16:21:33
- Latest transaction date: 2026-10-29 13:59:21

All records had valid INSTANCE_DATE values.

## 5. Missing Value Validation

The following important columns were checked:

| Column | Missing Values |
|---|---:|
| TRANSACTION_NUMBER | 0 |
| INSTANCE_DATE | 0 |
| PROCEDURE_EN | 0 |
| TRANS_VALUE | 0 |
| ACTUAL_AREA | 0 |

## 6. Numeric Value Validation

The following checks were performed:

| Column | Invalid or Non-positive Values |
|---|---:|
| TRANS_VALUE | 0 |
| ACTUAL_AREA | 0 |
| PROCEDURE_AREA | 2 |

The two records with blank PROCEDURE_AREA values are:

| Transaction Number | TRANS_VALUE | ACTUAL_AREA |
|---|---:|---:|
| 11-2671-2026 | 1,480,000 | 70.14 |
| 11-30754-2026 | 3,241,665.77 | 110.6 |

Both records have valid ACTUAL_AREA values.

## 7. Area Column Comparison

ACTUAL_AREA and PROCEDURE_AREA were compared.

- Records with matching area values: 127,309
- Records with different area values: 6,876
- Records with blank PROCEDURE_AREA: 2

Differences between the two area columns are not automatically treated as errors. Their business definitions should be confirmed.

## 8. Procedure Category Validation

The combined dataset contains 15 distinct PROCEDURE_EN categories.

All procedure categories were retained during the initial KPI calculations. No category was excluded.

## 9. KPI Validation Summary

The following provisional KPIs were calculated using all 134,185 records:

| KPI | Result |
|---|---:|
| Transaction Record Count | 134,185 |
| Total Transaction Value | 410,121,700,853.049 |
| Median Transaction Value | 1,410,000 |
| Median Price per Square Metre | 18,396.226567255 |

For Price per Square Metre, ACTUAL_AREA was selected provisionally.

The median rate using PROCEDURE_AREA was 18,423.9327579096, calculated from 134,183 valid records.

The ACTUAL_AREA definition should be confirmed against source documentation or mentor guidance.

The currency unit has not yet been verified and is therefore not labelled.

## 10. Data Handling Decisions

1. Original source CSV files were not modified.
2. No records were deleted during validation.
3. Repeated transaction numbers were retained because their meaning as unique transaction keys is not confirmed.
4. Blank PROCEDURE_AREA values were not replaced or estimated.
5. ACTUAL_AREA was used provisionally for the Price per Square Metre KPI because it was valid for all records.

## 11. Scope and Limitations

This report documents initial schema, record-count, transaction-number, date, selected missing-value, numeric-value, area-column, and procedure-category checks.

Further validation may be required for additional columns, category consistency, dashboard filters, and final KPI inclusion rules.

The analysis describes the supplied transaction records. It does not establish rental yield, occupancy, or guaranteed investment returns.
