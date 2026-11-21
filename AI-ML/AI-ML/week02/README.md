# Week 2 AI/ML Milestone Documentation: End-to-End Valuation Pipeline

**Project:** NEOSKILLZ DubaiEstate AI 360 – Agentic AI-Powered Real Estate Investment  
**Company:** NEOSKILLZ  
**Intern / Contributor:** Nitesh Kumar Barnwal  
**Domain:** Artificial Intelligence & Machine Learning (AI-ML)  
**Branch:** `feature/week02-aiml-nitesh`  
**Milestones Covered:** Day 8 (Dataset Scope), Day 9 (Preprocessing), Day 10 (Baseline Evaluation), Day 11 (Candidate Model Training), Day 12 (Error Diagnostics), Day 13 (Reusable Inference)  

---

## 1. Executive Summary & Pipeline Overview

The Week 2 AI/ML initiative transitions exploratory models into production-ready, leakage-free inference pipelines for predicting Dubai property transaction market values (`TRANS_VALUE`). The complete workflow comprises:

1. **Day 8 – Model Dataset & Eligibility:** Isolated 131,283 eligible arm's-length sale records from 134,185 raw transactions (`r"\bsell\b|\bsale\b"` with strictly positive price).
2. **Day 9 – Modular Preprocessing Pipeline (`preprocess.py`):** Built a high-throughput, leakage-free `ColumnTransformer` with median/most-frequent imputation and sparse one-hot encoding (375 features, <15 MB RAM).
3. **Day 10 – Baseline Model Evaluation (`baseline_model.ipynb`, `metrics.json`):** Established honest heuristic (`DummyRegressor`: MAE 1.88M AED) and simple parametric (`LinearRegression`: MAE 32.3M AED) benchmarks on an untouched chronological 20% test partition (26,257 records).
4. **Day 11 – Candidate Model Training (`candidate_model.ipynb`, `candidate_metrics.json`):** Trained a high-performance `RandomForestRegressor` with sensible regularization (`max_depth=12`, `min_samples_leaf=5`, `max_features='sqrt'`), reducing MAE by **22.73% vs. Dummy** and **95.49% vs. Linear Regression**.
5. **Day 12 – Model Error Diagnostics (`error_analysis.md`, `plots/`):** Segmented errors across asset classes and districts, revealing sub-840k AED MAE on residential apartments (84% of market) and error concentration in land and ultra-prime waterfront villas.
6. **Day 13 – Reusable Inference Module (`inference.py`):** Deployed a schema-validated `predict_price(sample)` function with input sanitization, error handling, and in-memory model caching.

---

## 2. Technical Architecture & Component Flow

```
                      Raw Dubai Transactions (134,185 records)
                                         │
                                         ▼
                  [Day 8 Filter] get_candidate_sales()
                  (Eligible Arm's-Length Sales: 131,283 records)
                                         │
                                         ▼
                              Chronological Partition
                  (Train: 80% [105,026]  |  Untouched Test: 20% [26,257])
                                         │
                 ┌───────────────────────┴───────────────────────┐
                 ▼                                               ▼
       prepare_features(train)                         prepare_features(test)
    - 2 Numeric Features                            - Drops TRANS_VALUE (target)
    - 11 Categorical Features                       - Drops TRANSACTION_NUMBER (id)
    - Target & IDs strictly excluded                - Target & IDs strictly excluded
                 │                                               │
                 ▼                                               │
    fit_preprocessor(X_train)                                    │
    ├── SimpleImputer(median) + StandardScaler()                 │
    └── SimpleImputer(most_frequent) + OneHotEncoder(sparse)     │
                 │                                               │
                 ├────────────────────── Frozen Preprocessor ────┤
                 ▼                                               ▼
           X_train_trans (105,026 × 375 CSR)               X_test_trans (26,257 × 375 CSR)
                 │                                               │
                 ▼                                               ▼
     RandomForestRegressor (Candidate)               Untouched Out-of-Sample Evaluation
    ├── n_estimators=100, max_depth=12               ├── Test MAE:  AED 1,455,828.87
    └── min_samples_leaf=5, max_features='sqrt'      └── Test RMSE: AED 8,501,841.09
                 │
                 ▼
       Persisted Pipeline Artifact
     `models/candidate_pipeline.joblib`
                 │
                 ▼
      [Day 13] Reusable Inference API
      `predict_price(sample)` in `inference.py`
```

---

## 3. Benchmark Model Comparison Summary

Evaluated on the exact same untouched chronological test partition ($N = 26,257$ transactions; August 18, 2026 to October 29, 2026):

| Model Name | Model Class / Configuration | Test MAE (AED) | Test RMSE (AED) | MAE Gain vs. Heuristic | Notes & Diagnostic Observations |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **DummyRegressor (Median)** | Naive Constant: `AED 1,450,000` | 1,884,136.43 | 9,815,454.11 | Baseline | Core heuristic benchmark to beat. |
| **DummyRegressor (Mean)** | Naive Constant: `AED 3,138,379` | 2,547,931.28 | 9,739,962.56 | -35.23% | Distorted by multi-million dirham luxury outliers. |
| **LinearRegression (OLS)** | Ordinary Least Squares (`fit_intercept=True`) | 32,295,767.40 | 184,340,582.93 | -1,614.09% | Severe variance catastrophe on novel categorical dummy combinations. |
| **RandomForestRegressor** | Ensemble: `depth=12, leaf=5, feat=sqrt` | **1,455,828.87** | **8,501,841.09** | **+22.73%** | **Best overall candidate model.** Sub-839k MAE on residential apartments. |

---

## 4. Reusable Inference API (`inference.py`)

The inference function `predict_price(sample)` accepts either a single property dictionary or a multi-row pandas DataFrame.

### Example Usage:

```python
from inference import predict_price

property_sample = {
    "PROCEDURE_AREA": 125.0,
    "ACTUAL_AREA": 120.0,
    "PROCEDURE_EN": "Sale",
    "IS_OFFPLAN_EN": "Ready",
    "IS_FREE_HOLD_EN": "Free Hold",
    "USAGE_EN": "Residential",
    "AREA_EN": "JUMEIRAH VILLAGE CIRCLE",
    "PROP_TYPE_EN": "Unit",
    "PROP_SB_TYPE_EN": "Flat",
    "ROOMS_EN": "2 B/R",
    "NEAREST_METRO_EN": "DAMAC Metro Station",
    "NEAREST_MALL_EN": "Mall of the Emirates",
    "NEAREST_LANDMARK_EN": "Burj Khalifa",
}

# Predict property valuation
predicted_price = predict_price(property_sample)
print(f"Predicted Valuation: AED {predicted_price:,.2f}")
# Output: Predicted Valuation: AED 2,241,127.00
```

### Input Validation & Safeguards:
- Rejects missing required features (`ValueError: Missing required feature(s): ...`).
- Rejects negative, zero, or non-numeric area values (`ValueError: ... strictly positive (> 0)`).
- Rejects target or identifier leakage fields (`TRANS_VALUE`, `TRANSACTION_NUMBER`).
- Gracefully encodes novel unseen categories via `OneHotEncoder(handle_unknown='ignore')`.
- Filters unexpected extra columns by default or enforces strict validation (`strict_fields=True`).

---

## 5. Verification & Test Execution

Run the complete test suite (24 passing unit and integration tests across preprocessing and inference):

```bash
# Run all Week 2 tests
pytest AI-ML/AI-ML/week02/tests/ -v

# Run individual suites
pytest AI-ML/AI-ML/week02/tests/test_preprocess.py -v
pytest AI-ML/AI-ML/week02/tests/test_inference.py -v

# Run standalone inference smoke test
python AI-ML/AI-ML/week02/inference.py
```

### Test Coverage Highlights:
- **Preprocessing (14 Tests):** Numeric/categorical missing imputation, consistent dimensions, zero NaNs/Infs, target/identifier leakage blocking, NotFittedError enforcement, sparse matrix operations, real 134k-record slice integration.
- **Inference (10 Tests):** Valid dict/DataFrame inputs, missing feature detection, strict vs. lenient unexpected fields, negative/zero value rejection, unseen category handling, empty input handling, pipeline reload reproducibility.

---

## 6. Repository Artifacts Inventory

- [`model_dataset.py`](model_dataset.py): Source loader & procedure analysis.
- [`modeling_scope.md`](modeling_scope.md): Modeling scope and eligibility specification.
- [`preprocess.py`](preprocess.py): Preprocessing module and ColumnTransformer builder.
- [`baseline_model.ipynb`](baseline_model.ipynb): Day 10 baseline regression experiment notebook.
- [`metrics.json`](metrics.json): Day 10 baseline benchmark metrics.
- [`candidate_model.ipynb`](candidate_model.ipynb): Day 11 candidate Random Forest experiment notebook.
- [`candidate_metrics.json`](candidate_metrics.json): Day 11 candidate model metrics.
- [`error_analysis.md`](error_analysis.md): Day 12 diagnostic report by property type and district.
- [`plots/`](plots/): Diagnostic charts (`actual_vs_predicted.png`, `error_by_property_type.png`, `error_by_area.png`).
- [`inference.py`](inference.py): Day 13 reusable valuation API.
- [`models/candidate_pipeline.joblib`](models/candidate_pipeline.joblib): Serialized model pipeline artifact.
- [`tests/test_preprocess.py`](tests/test_preprocess.py): Day 9 test suite.
- [`tests/test_inference.py`](tests/test_inference.py): Day 13 test suite.
