# DubaiEstate-AI-360-Agentic-AI-Powered-Real-Estate-Investment
Agentic AI-powered real estate intelligence platform for property investment analysis, brokerage automation, lead intelligence, property management, forecasting and decision support.

# DubaiEstate AI 360° — Day 1

## Overview

Day 1 focused on understanding the Dubai real estate transaction datasets, defining the prediction target, identifying potential comparable sales, and selecting suitable features for future analysis.

## Dataset Inspection

* Inspected two datasets containing **127,000** and **7,185** records.
* Checked column names, data types, missing values, and duplicate records.
* Verified that `TRANS_VALUE` contains no missing, zero, or negative values in either dataset.

## Target Variable

* **Target:** `TRANS_VALUE`
* This variable represents the transaction value to be predicted.

## Feature Selection

Selected 10 provisional predictors:
`AREA_EN`, `PROP_TYPE_EN`, `PROP_SB_TYPE_EN`, `ACTUAL_AREA`, `ROOMS_EN`, `PARKING`, `IS_OFFPLAN_EN`, `IS_FREE_HOLD_EN`, `USAGE_EN`, and `PROJECT_EN`.

Excluded identifiers and initially unsuitable columns, including `TRANSACTION_NUMBER`, `GROUP_EN`, `TOTAL_BUYER`, `TOTAL_SELLER`, and `MASTER_PROJECT_EN`. `INSTANCE_DATE` is reserved for chronological splitting in a later stage.

## Comparable-Sales Audit

* Dataset 1 contains **120,553 candidate records (94.92%)** with procedure labels `Sale` or `Sell - Pre registration`.
* Dataset 2 contains no records with these exact labels.
* Other transaction procedures require further review before confirming comparable-sales eligibility.

## Outcome

Completed initial dataset validation, target definition, provisional feature selection, and comparable-sales auditing. No original records were deleted or modified.

**Note:** Comparable-sales eligibility and final feature suitability remain provisional pending further validation.
