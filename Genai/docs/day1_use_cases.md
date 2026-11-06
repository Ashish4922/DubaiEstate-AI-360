# GenAI Day 1: Use Cases and Boundaries

**Domain:** GenAI | **Week:** 1 | **Day:** 1

## 1. Purpose
A property-information assistant that answers questions about Dubai
transaction data. Every figure is computed by Python code from the project
dataset. The language model, if used, only phrases verified results.

## 2. Data source
- Files: `DataSets/dubai_transactions_2026_part_1.csv` (127,000 rows) and
  `DataSets/dubai_transactions_2026_part_2.csv` (7,185 rows)
- Both files share the same 22 columns. Original files are read-only.
- Combined rows: 134,185 (before deduplication)
- Date coverage: 2026-01-01 to 2026-10-29. October 2026 is a partial month.
- Inspected on: [today's date, 6 Nov 2026]
- Known quality notes:
  - 24 duplicate TRANSACTION_NUMBER values (handling decided after review)
  - PROP_SB_TYPE_EN has 1,594 blanks and overlapping residential labels
  - GROUP_EN contains only "Sales" in this extract
  - No zero or missing values in TRANS_VALUE or ACTUAL_AREA

## 3. Fields used
| Purpose                             | Column                         |
|-------------------------------------|--------------------------------|
| Transaction identifier              | TRANSACTION_NUMBER             |
| Date                                | INSTANCE_DATE                  |
| Transaction group (filter to Sales) | GROUP_EN                       |
| Price (AED)                         | TRANS_VALUE                    |
| Size (sq m)                         | ACTUAL_AREA                    |
| Location                            | AREA_EN                        |
| Property category / subtype         | PROP_TYPE_EN / PROP_SB_TYPE_EN |
| Off-plan status                     | IS_OFFPLAN_EN                  |

Price per square metre = TRANS_VALUE / ACTUAL_AREA, only where both are
greater than zero.

## 4. Five grounded user questions
| # | Question                                                        | Fields                                 | Calculation                   | Filters               |
|---|-----------------------------------------------------------------|----------------------------------------|-------------------------------|-----------------------|
| 1 | How many sales transactions were recorded each month?           |INSTANCE_DATE, GROUP_EN                 | Count by month                | GROUP_EN = Sales      |
| 2 | What is the median sale value of flats in [area]?               |AREA_EN, PROP_SB_TYPE_EN, TRANS_VALUE   | Median                        | Sales,valid value>0   |
| 3 | Which five areas had the most sales transactions?               |AREA_EN                                 | Count, top 5, show sample size| Sales                 |
| 4 | How does median price per sq m compare between [area A] and [area B]?|AREA_EN, TRANS_VALUE, ACTUAL_AREA | Median of value / area        | Sales,value>0, area>0  |
| 5 | What share of sales were off-plan versus ready?                 |IS_OFFPLAN_EN                           | Percentage of count           | Sales                 |

## 5. Required behaviour when data is missing
- Area not found: say so and suggest similar names from the 253 areas in the data.
- Fewer than 30 matching transactions: report the count and warn that the
  sample is too small for a reliable median. (30 is a project-chosen
  convention, not a statistical guarantee.)
- Date outside 2026-01-01 to 2026-10-29: state the actual coverage.
- Monthly figures: label October 2026 as a partial month.
- Price per sq m: calculated for property type "Unit" only. Land and Building
  rows are excluded and the answer must say so.
- Blank property subtype: report as "Not specified", never guess a subtype.

## 6. Prohibited behaviours
- No guaranteed, predicted or implied returns, appreciation or future prices
- No buy, sell or invest recommendations
- No rental yield, occupancy, tenancy or maintenance claims (fields not in dataset)
- No figure that was not computed from the dataset
- No personal or restricted data sent to external APIs

## 7. Answer requirements
Every answer must include: the figure, the unit (AED, sq m, count), the
filters applied, the sample size, the date coverage, and a short uncertainty note.

## 8. Standard disclaimer
This is a learning prototype. Figures describe historical transactions only
and are not investment advice.