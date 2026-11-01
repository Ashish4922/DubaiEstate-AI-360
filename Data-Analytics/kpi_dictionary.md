# KPI Dictionary – Dubai Real Estate Transactions

## 1. Dataset Scope

- Source files: dubai_transactions_2026_part_1.csv and dubai_transactions_2026_part_2.csv
- Combined records: 134,185
- Date coverage: 01 January 2026 to 29 October 2026
- All 15 procedure categories are included.
- Original source CSV files remain unchanged.
- No records have been removed based on repeated transaction numbers.

## 2. Transaction Record Count

**Definition:** Counts the number of transaction records included in the analysis.

**Formula:**

Transaction Record Count = COUNT of included dataset rows

**Current result:** 134,185 records

**Inclusion rules:**
- Include all records from both source files.
- Do not automatically remove repeated transaction numbers.
- Repeated transaction numbers require confirmation of the source transaction-key definition before deduplication.

## 3. Total Transaction Value

**Definition:** Calculates the sum of transaction values across all included records.

**Formula:**

Total Transaction Value = SUM(TRANS_VALUE)

**Current result:** 410,121,700,853.049

**Inclusion rules:**
- Include all 134,185 records.
- Use the TRANS_VALUE column.
- No records are excluded based on property type or procedure category.

**Note:** The currency unit must be confirmed from source documentation before assigning a currency label.

## 4. Median Transaction Value

**Definition:** Represents the middle transaction value after sorting all included transaction values in ascending order.

**Formula:**

Median Transaction Value = MEDIAN(TRANS_VALUE)

**Current result:** 1,410,000

**Inclusion rules:**
- Include all 134,185 records.
- Use valid TRANS_VALUE values.
- No records are excluded based on procedure category.

## 5. Median Price per Square Metre

**Definition:** Represents the median of individual transaction prices per square metre.

**Formula:**

Price per Square Metre = TRANS_VALUE / ACTUAL_AREA

Median Price per Square Metre = MEDIAN of individual Price per Square Metre values.

**Current result:** 18,396.226567255

**Inclusion rules:**
- Use TRANS_VALUE as the transaction value.
- Use ACTUAL_AREA as the area denominator.
- Include records with valid, positive transaction values and actual areas.
- All 134,185 records have valid TRANS_VALUE and ACTUAL_AREA values.
- No records are excluded for this KPI.

**Area column comparison:**
- ACTUAL_AREA median rate: 18,396.226567255
- PROCEDURE_AREA median rate: 18,423.9327579096
- Valid PROCEDURE_AREA records: 134,183
- Two records have blank PROCEDURE_AREA values.

**Decision:** ACTUAL_AREA is the provisional denominator because it is valid for all records and represents actual area. This definition should be confirmed against source documentation or the mentor's guidance.

## 6. Important Limitations

1. Repeated transaction numbers have not been removed because their meaning as unique transaction keys is not confirmed.
2. The currency unit has not yet been verified.
3. The selected area denominator is provisional pending source or mentor confirmation.
4. These KPIs describe the supplied transaction records; they do not represent rental yield, occupancy, or guaranteed investment returns.
5. KPI results may change if the source definitions or inclusion rules are revised.

---
