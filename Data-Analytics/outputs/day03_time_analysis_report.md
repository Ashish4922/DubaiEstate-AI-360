# Day 3: Time-Based Transaction Analysis

## Objective
Analyze monthly transaction counts and total transaction values.

## Dataset Overview
- Total source records: 134,185
- Records with valid dates and values: 134,185
- Analysis start date: 2026-01-01
- Analysis end date: 2026-10-29
- Earliest date: 2026-01-01 16:21:33
- Latest date: 2026-10-29 13:59:21

## Monthly Results
  MONTH  transaction_count total_transaction_value median_transaction_value
2026-01              17400       72,198,019,444.70             1,845,399.00
2026-02              17015       60,741,459,408.11             1,684,047.00
2026-03              13496       43,587,041,629.99             1,673,858.00
2026-04              14011       48,100,023,837.79             1,700,000.00
2026-05              10266       28,877,221,051.01             1,206,656.00
2026-06              13927       33,206,390,884.30             1,157,099.64
2026-07              14138       34,922,419,513.01             1,137,420.00
2026-08              11813       27,746,508,879.18             1,200,000.00
2026-09              11182       28,778,441,783.19             1,319,915.85
2026-10              10937       31,964,174,421.77             1,400,000.00

## Key Observations
- Months analyzed: 10
- Highest transaction-count month: 2026-01
- Lowest transaction-count month: 2026-05
- Highest transaction-value month: 2026-01
- Lowest transaction-value month: 2026-08
- Total transaction records: 134,185
- Total transaction value: 410,121,700,853.05

## Data Reconciliation
- Monthly record count: 134,185
- Filtered source record count: 134,185
- Monthly count matches filtered source records: True

## Data Limitations
- Latest month is partial as of 2026-10-29.
- Monthly totals describe recorded transaction values, not property returns or rental income.
- Transaction counts represent source records; repeated transaction IDs were retained because their unique-key meaning has not been confirmed.
- Currency unit has not been independently verified.

## Output Files
- day03_monthly_summary.csv
- day03_monthly_transaction_count.png
- day03_monthly_transaction_value.png