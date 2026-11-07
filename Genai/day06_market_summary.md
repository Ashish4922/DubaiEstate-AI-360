# Dubai Real Estate Transaction Market Summary

## Reporting scope

- Source files: 2 CSV files
- Total source records: 134,185
- Sales records: 134,185
- Reporting period: 2026-01-01 16:21:33 to 2026-10-29 13:59:21
- Dataset: Dubai transaction CSV files for 2026

## Dataset-level findings

- Valid positive-value sales: 134,185
- Total transaction value: AED 410,121,700,853.05
- Average transaction value: AED 3,056,390.06
- Median transaction value: AED 1,410,000.00
- Minimum transaction value: AED 163.35
- Maximum transaction value: AED 3,130,254,657.13
- Valid price-per-sqm records: 134,185
- Median price per sqm: AED 18,396.23
- Average price per sqm: AED 20,599.68

## Area comparison

Top 10 areas by transaction count among records with positive transaction values and positive ACTUAL_AREA:

| Area | Transaction count | Median AED/sqm |
|---|---:|---:|
| Madinat Al Mataar | 12,775 | 18,178.99 |
| JUMEIRAH VILLAGE CIRCLE | 8,602 | 15,750.42 |
| DUBAI LAND RESIDENCE COMPLEX | 5,219 | 15,347.33 |
| BUSINESS BAY | 5,152 | 25,960.47 |
| MAJAN | 4,424 | 15,459.83 |
| Al Yelayiss 1 | 3,927 | 19,611.11 |
| Al Hebiah Fifth | 3,215 | 18,521.86 |
| Palm Deira | 3,198 | 30,390.08 |
| Jabal Ali First | 2,908 | 17,482.22 |
| ARJAN | 2,844 | 17,030.31 |

## Methodology

- Read both original CSV files without modifying them.
- Include rows with GROUP_EN equal to Sales.
- Transaction-value statistics use positive TRANS_VALUE values.
- Price-per-sqm statistics require positive TRANS_VALUE and positive ACTUAL_AREA.
- Price per sqm is calculated as TRANS_VALUE / ACTUAL_AREA.
- Median is used to reduce sensitivity to extreme values.
- Area rankings use transaction count, not price.
- Original CSV row numbers include the header as row 1.

## Source references

Aggregate figures are reproducible from the source CSVs using the accompanying Python script.

- Record-level evidence: `day06_source_evidence.csv`
- Evidence file includes source CSV filename, original CSV row, transaction number, date, area, value and price per sqm.

## Limitations

- Dataset coverage ends at the latest date shown above.
- Dataset figures may not represent every Dubai transaction.
- Transaction values and price-per-sqm distributions contain extreme observations.
- Price per sqm uses ACTUAL_AREA; it may differ from other area definitions.
- This is descriptive historical analysis, not investment advice.
- No future returns or price forecasts are estimated.
