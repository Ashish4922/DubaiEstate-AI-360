# Week 2 – Day 12: Model Error Analysis Report

**Project:** NEOSKILLZ DubaiEstate AI 360 – Agentic AI-Powered Real Estate Investment  
**Intern / Contributor:** Nitesh Kumar Barnwal  
**Domain:** Artificial Intelligence & Machine Learning (AI-ML)  
**Milestone:** Week 2 – Day 12: Model Error Diagnostics & Segment Analysis  
**Branch:** `feature/week02-aiml-nitesh`  
**Evaluation Set:** Untouched Out-of-Sample Test Partition ($N = 26,257$ transactions; August 18, 2026 to October 29, 2026)  
**Evaluated Model:** `RandomForestRegressor` (`n_estimators=100`, `max_depth=12`, `min_samples_leaf=5`, `max_features='sqrt'`)  

---

## 1. Executive Summary & Diagnostic Scope

The purpose of Day 12 is to dissect where the candidate `RandomForestRegressor` performs with high precision and where prediction errors remain elevated. Across the entire out-of-sample test partition ($N = 26,257$ transactions), the candidate model achieved:
- **Mean Absolute Error (MAE):** `AED 1,455,828.87` (22.73% improvement over Naive Median, 95.49% improvement over Linear Regression)
- **Median Absolute Error (MedAE):** `AED 641,632.56`
- **Root Mean Squared Error (RMSE):** `AED 8,501,841.09`

While macro-level metrics demonstrate substantial improvement over Day 10 baselines, aggregate figures mask dramatic variation across asset classes and geographic zones. This report segments the test predictions by **Property Type** and **District Area**, isolating the structural factors driving valuation errors.

---

## 2. Global Error Profile & Visualizations

The prediction error distribution is characterized by high precision across the core residential mass market, combined with a heavy right tail driven by ultra-luxury waterfront estates and multi-hectare commercial plots.

### Visual Diagnostics Generated:
1. **Actual vs. Predicted Scatter:** [`plots/actual_vs_predicted.png`](plots/actual_vs_predicted.png)  
   Illustrates model calibration against the perfect appraisal line ($y = x$). For values below 10M AED, predictions cluster closely along the diagonal; above 15M AED, predictions show systematic under-prediction as tree leaves constrain extreme luxury valuations.
2. **Error by Property Type:** [`plots/error_by_property_type.png`](plots/error_by_property_type.png)  
   Contrasts MAE and MedAE across `Unit`, `Building`, and `Land`.
3. **Error by Geographic District:** [`plots/error_by_area.png`](plots/error_by_area.png)  
   Surfaces MAE across the Top 15 most active Dubai communities ($N \ge 30$).

---

## 3. Error Analysis by Property Type

Real estate in Dubai spans three distinct legal classifications with radically different pricing mechanisms:

| Property Type (`PROP_TYPE_EN`) | Test Count ($N$) | % of Test Set | Mean Actual Price (AED) | Median Actual Price (AED) | Model MAE (AED) | Model MedAE (AED) | Model RMSE (AED) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`Unit`** (Apartments / Flatted Villas) | **22,064** | **84.03%** | 1,819,132.30 | 1,199,847.00 | **838,617.13** | **604,879.52** | 6,392,153.97 |
| **`Building`** (Whole Residential/Comm) | **1,739** | **6.62%** | 4,646,950.07 | 3,675,000.00 | **1,580,433.58** | **814,222.52** | 17,195,927.60 |
| **`Land`** (Commercial & Residential Plots)| **2,454** | **9.35%** | 9,575,926.69 | 4,865,113.79 | **6,916,901.52** | **4,453,986.07** | 14,016,828.93 |

### Critical Findings:
1. **High Precision on Core Residential Units:**
   For typical residential units ($84.03\%$ of the Dubai market), the candidate model achieves an outstanding **MAE of AED 838,617.13** and a **MedAE of AED 604,879.52**. Standard apartments and flats follow consistent per-square-meter pricing trajectories well-captured by area and room count.
2. **Severe Error Concentration in Land Transactions:**
   `Land` transactions represent only $9.35\%$ of volume but generate an **MAE of AED 6.92M** and **RMSE of AED 14.02M**. Plot pricing depends heavily on Floor Area Ratio (FAR), Gross Floor Area (GFA) allowances, master developer infrastructure commitments, and zoning entitlements—attributes not captured in the 13 baseline features.
3. **Whole Buildings Exhibit Moderate Error with Heavy Tail:**
   `Building` transactions exhibit a competitive Median Absolute Error (AED 814k), but a elevated RMSE (AED 17.20M) due to bulk portfolio sales and commercial towers that sell for tens of millions of AED.

---

## 4. Error Analysis by Geographic District (`AREA_EN`)

To avoid statistical distortion from micro-sample outliers, geographic districts are segmented into high-volume active areas ($N \ge 30$) and low-frequency outlier groups ($N < 30$).

### A. High-Volume Active Communities (Top 15 by Transaction Volume):

| District Name (`AREA_EN`) | Test Count ($N$) | Mean Actual Price (AED) | Median Actual Price (AED) | MAE (AED) | MedAE (AED) | RMSE (AED) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Madinat Al Mataar** | 2,266 | 1,385,971.90 | 745,375.00 | **622,764.13** | 530,337.80 | 1,807,360.17 |
| **Jumeirah Village Circle (JVC)** | 1,871 | 1,372,834.48 | 984,225.06 | **765,880.36** | 562,486.37 | 4,087,916.18 |
| **Business Bay** | 987 | 3,523,029.18 | 2,000,000.00 | **1,493,667.19** | 734,146.81 | 3,768,699.86 |
| **Majan** | 930 | 1,013,854.02 | 770,006.00 | **617,913.54** | 550,067.44 | 1,250,338.61 |
| **Al Hebiah Fifth** | 904 | 1,969,240.83 | 1,418,000.00 | **1,549,794.66** | 698,158.53 | 2,075,843.18 |
| **Dubai Land Residence Complex** | 826 | 1,232,931.27 | 800,000.00 | **740,363.19** | 498,123.79 | 3,773,807.27 |
| **Al Rowaiyah First** | 730 | 4,824,377.65 | 3,392,500.00 | **6,809,143.45** | 7,667,123.68 | 9,919,049.84 |
| **Jabal Ali Industrial Second** | 722 | 1,192,509.02 | 807,250.87 | **843,374.37** | 663,196.81 | 1,023,113.61 |
| **City of Arabia** | 710 | 1,125,692.07 | 1,020,100.00 | **608,310.76** | 608,658.36 | 672,477.94 |
| **Arjan** | 550 | 1,144,865.12 | 992,500.00 | **649,982.22** | 567,815.86 | 1,163,632.07 |
| **Al Hebiah First** | 544 | 1,752,997.02 | 1,050,000.00 | **734,305.15** | 628,684.07 | 859,702.85 |
| **Al Yufrah 1** | 517 | 4,081,855.87 | 2,650,000.00 | **1,073,481.63** | 803,223.74 | 1,325,272.30 |
| **Down Town Jabal Ali** | 513 | 1,291,043.39 | 1,106,998.65 | **752,741.24** | 675,207.17 | 1,462,883.48 |
| **Al Khairan First** | 512 | 2,920,730.63 | 2,983,388.00 | **701,091.72** | 584,619.54 | 902,816.04 |
| **Jabal Ali First** | 447 | 2,395,183.88 | 1,959,801.00 | **855,248.33** | 412,953.12 | 1,469,080.58 |

### B. Top 5 Lowest-Error Communities ($N \ge 30$):
Communities where property appraisal is most reliable:
1. **Sufouh Gardens** ($N = 65$): **MAE AED 377,352.22** | MedAE AED 323,159.98
2. **Horizon** ($N = 136$): **MAE AED 405,835.72** | MedAE AED 263,534.65
3. **Falcon City of Wonders** ($N = 51$): **MAE AED 466,037.76** | MedAE AED 376,953.33
4. **Al Kifaf** ($N = 110$): **MAE AED 492,665.23** | MedAE AED 448,036.30
5. **Business Park** ($N = 203$): **MAE AED 528,081.76** | MedAE AED 309,090.59

### C. Top 5 Highest-Error Communities ($N \ge 30$):
Communities requiring specialized sub-models or manual appraisal escalation:
1. **Al Rowaiyah First** ($N = 730$): **MAE AED 6,809,143.45** (Large agricultural and industrial commercial plots)
2. **Palm Jabal Ali** ($N = 93$): **MAE AED 6,657,005.93** | Mean Actual AED 19.96M (Off-plan luxury waterfront mega-villas)
3. **Palm Jumeirah** ($N = 188$): **MAE AED 6,515,015.74** | Mean Actual AED 14.54M (Ultra-prime luxury villas with private beach frontage)
4. **Al Hebiah Fourth** ($N = 56$): **MAE AED 5,834,178.03** | Mean Actual AED 15.93M (High-end golf course villas)
5. **Burj Khalifa** ($N = 385$): **MAE AED 3,513,355.55** | MedAE AED 778,291.88 (Penthouse units with view premiums)

---

## 5. Avoiding Misleading Conclusions from Small Sample Groups ($N < 30$)

Reviewing raw district MAE tables without sample size thresholds exposes extreme anomalies:
- **Al Goze Industrial Third:** Recorded an apparent astronomical MAE of **AED 146,332,433.74**.
  - *Context:* This represents a **single isolated commercial warehouse transaction** ($N = 1$) selling for **AED 191,200,000.00**.
- **Al Nahda First:** Recorded an apparent MAE of **AED 88,704,465.39** ($N = 3$).
- **Al Qusais Industrial Second:** Recorded an apparent MAE of **AED 84,814,705.06** ($N = 1$).

> [!WARNING]
> Drawing conclusions regarding model inadequacy for entire districts based on $N \le 3$ transactions is statistically invalid. These records represent specialized industrial plots and corporate campus acquisitions that should be filtered into an institutional asset class rather than treated as standard residential transactions.

---

## 6. Identified Root Causes & Technical Limitations

1. **Non-Linear Luxury Premium (The "Billionaire Tail"):**
   Tree ensembles using mean square error or standard splits tend to predict conservative leaf means. For trophy properties on Palm Jumeirah selling above 50M AED, the model predicts between 12M and 25M AED, producing large absolute residuals.
2. **Missing Architectural & Amenity Metadata:**
   The current 13 features include physical area (`ACTUAL_AREA`) and room counts (`ROOMS_EN`), but lack floor elevation, sea vs. community view designations, furnished status, and private pool availability.
3. **Spatial Feature Sparsity in Emerging Master Projects:**
   Proximity features (`NEAREST_METRO_EN`, `NEAREST_MALL_EN`) have ~50% missing values in nascent developing sectors (e.g., Al Rowaiyah, Madinat Al Mataar). Imputing the most frequent category reduces geographic granularity.

---

## 7. Actionable Recommendations for Downstream Sprint

1. **Implement Segment-Specific Sub-Models:**
   Train separate dedicated regressors for `Unit` (residential apartments) versus `Land` / `Building` assets.
2. **Target Transformation:**
   Apply $\log(1 + y)$ target transformation in future iterations to penalize proportional rather than absolute dirham error, stabilizing leaf predictions on multi-million dirham transactions.
3. **Escalation Threshold in Inference:**
   For transactions flagged as `Land` or predicted value $> 20\text{M AED}$, tag predictions with an `'Appraisal Uncertainty: HIGH'` flag for secondary human review.
