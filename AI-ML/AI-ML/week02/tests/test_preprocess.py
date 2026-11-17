"""
Unit and Integration Tests for Week 2 Day 9 Preprocessing Pipeline.
Project: DubaiEstate AI 360 – Agentic AI-Powered Real Estate Investment
Intern: Nitesh Kumar Barnwal
Branch: feature/week02-aiml-nitesh

Coverage:
1. Numeric missing-value imputation (median).
2. Categorical missing-value imputation (most_frequent).
3. Handling unknown/unseen categories in validation/test data (handle_unknown='ignore').
4. Transformed feature dimension consistency across splits.
5. Verification of zero NaN and zero infinite values.
6. Ensuring preprocessor is fitted strictly on training data (NotFittedError, parameter purity).
7. Target leakage prevention (TRANS_VALUE excluded and detected).
8. Identifier leakage prevention (TRANSACTION_NUMBER excluded and detected).
9. Sparse matrix compatibility (CSR output, operations, dense fallback).
10. End-to-end integration test on approved dataset sample.
"""

from pathlib import Path
import sys
from typing import Dict

import numpy as np
import pandas as pd
import pytest
from scipy import sparse
from sklearn.exceptions import NotFittedError

# Ensure week02 directory is available in sys.path
WEEK02_DIR = Path(__file__).resolve().parents[1]
if str(WEEK02_DIR) not in sys.path:
    sys.path.insert(0, str(WEEK02_DIR))

from preprocess import (
    ALL_FEATURES,
    CATEGORICAL_FEATURES,
    IDENTIFIER_COLUMN,
    NUMERIC_FEATURES,
    TARGET_COLUMN,
    build_preprocessor,
    check_transformed_matrix,
    fit_preprocessor,
    fit_transform_features,
    get_candidate_sales,
    prepare_features,
    transform_features,
)


@pytest.fixture
def sample_raw_data() -> pd.DataFrame:
    """Fixture providing representative synthetic transaction records."""
    return pd.DataFrame({
        "TRANSACTION_NUMBER": ["TX-101", "TX-102", "TX-103", "TX-104", "TX-105", "TX-106"],
        "INSTANCE_DATE": [
            "2026-01-01 10:00:00",
            "2026-01-02 11:30:00",
            "2026-01-03 14:15:00",
            "2026-01-04 09:45:00",
            "2026-01-05 16:00:00",
            "2026-01-06 18:20:00",
        ],
        "TRANS_VALUE": [1200000.0, 1850000.0, 950000.0, 2400000.0, 3100000.0, 1450000.0],
        "PROCEDURE_AREA": [85.5, 120.0, np.nan, 180.0, 220.0, 95.0],
        "ACTUAL_AREA": [80.0, np.nan, 90.0, 175.0, 210.0, 92.0],
        "PROCEDURE_EN": [
            "Sell - Pre registration",
            "Sale",
            "Sell - Pre registration",
            "Sale",
            "Sell - Pre registration",
            "Sale",
        ],
        "IS_OFFPLAN_EN": ["Off-Plan", "Ready", "Off-Plan", "Ready", "Off-Plan", "Ready"],
        "IS_FREE_HOLD_EN": ["Free Hold", "Free Hold", "Non Free Hold", "Free Hold", "Free Hold", "Free Hold"],
        "USAGE_EN": ["Residential", "Residential", "Commercial", "Residential", "Residential", "Commercial"],
        "AREA_EN": ["Downtown", "Dubai Marina", "Downtown", "Business Bay", "Dubai Marina", "Downtown"],
        "PROP_TYPE_EN": ["Unit", "Unit", "Villa", "Unit", "Building", "Unit"],
        "PROP_SB_TYPE_EN": ["Flat", "Flat", "Villa", "Flat", "Building", "Flat"],
        "ROOMS_EN": ["1 B/R", "2 B/R", "3 B/R", "2 B/R", np.nan, "1 B/R"],
        "NEAREST_METRO_EN": ["Burj Khalifa", "DAMAC", "Burj Khalifa", np.nan, "DAMAC", "Burj Khalifa"],
        "NEAREST_MALL_EN": ["Dubai Mall", "Marina Mall", "Dubai Mall", "Dubai Mall", np.nan, "Dubai Mall"],
        "NEAREST_LANDMARK_EN": ["Burj Khalifa", "Marina Walk", "Burj Khalifa", "Creek", "Marina Walk", np.nan],
    })


def test_prepare_features_schema_and_purity(sample_raw_data: pd.DataFrame):
    """Verify prepare_features selects all permitted features and drops metadata."""
    X = prepare_features(sample_raw_data)

    assert isinstance(X, pd.DataFrame)
    assert X.shape == (6, len(ALL_FEATURES))
    assert list(X.columns) == ALL_FEATURES
    assert TARGET_COLUMN not in X.columns
    assert IDENTIFIER_COLUMN not in X.columns
    assert "INSTANCE_DATE" not in X.columns


def test_prepare_features_with_target(sample_raw_data: pd.DataFrame):
    """Verify prepare_features returns tuple (X, y) when return_target=True."""
    X, y = prepare_features(sample_raw_data, return_target=True)

    assert isinstance(X, pd.DataFrame)
    assert isinstance(y, pd.Series)
    assert len(X) == len(y) == 6
    assert TARGET_COLUMN not in X.columns
    assert y.name == TARGET_COLUMN
    assert (y == sample_raw_data["TRANS_VALUE"]).all()


def test_prepare_features_input_validation():
    """Verify prepare_features raises appropriate errors on invalid inputs."""
    with pytest.raises(TypeError, match="pandas DataFrame"):
        prepare_features([1, 2, 3])  # type: ignore

    invalid_df = pd.DataFrame({"PROCEDURE_AREA": [100.0]})
    with pytest.raises(ValueError, match="Missing required feature columns"):
        prepare_features(invalid_df)


def test_numeric_missing_value_imputation():
    """Verify numeric columns are imputed with training median."""
    train_df = pd.DataFrame({
        "PROCEDURE_AREA": [100.0, 200.0, 300.0],  # Median = 200.0
        "ACTUAL_AREA": [50.0, 70.0, 90.0],        # Median = 70.0
    })
    test_df = pd.DataFrame({
        "PROCEDURE_AREA": [np.nan],
        "ACTUAL_AREA": [np.nan],
    })

    # Test with unscaled numeric features to directly verify imputed values
    preprocessor = build_preprocessor(
        numeric_features=["PROCEDURE_AREA", "ACTUAL_AREA"],
        categorical_features=[],
        scale_numeric=False,
        sparse_output=False,
    )
    fit_preprocessor(preprocessor, train_df)
    transformed_test = transform_features(preprocessor, test_df)

    assert transformed_test.shape == (1, 2)
    assert np.isclose(transformed_test[0, 0], 200.0)
    assert np.isclose(transformed_test[0, 1], 70.0)
    assert not np.isnan(transformed_test).any()


def test_categorical_missing_value_imputation():
    """Verify categorical columns are imputed with most frequent category from training."""
    train_df = pd.DataFrame({
        "AREA_EN": ["Dubai Marina", "Downtown", "Dubai Marina", "Dubai Marina"],  # Most frequent: Dubai Marina
        "USAGE_EN": ["Residential", "Commercial", "Residential", "Residential"],   # Most frequent: Residential
    })
    test_df = pd.DataFrame({
        "AREA_EN": [None],
        "USAGE_EN": [np.nan],
    })

    preprocessor = build_preprocessor(
        numeric_features=[],
        categorical_features=["AREA_EN", "USAGE_EN"],
        sparse_output=False,
    )
    fit_preprocessor(preprocessor, train_df)
    transformed_test = transform_features(preprocessor, test_df)

    # Imputed values should match "Dubai Marina" and "Residential"
    encoder = preprocessor.named_transformers_["categorical"].named_steps["encoder"]
    area_categories = list(encoder.categories_[0])
    usage_categories = list(encoder.categories_[1])

    expected_area_idx = area_categories.index("Dubai Marina")
    expected_usage_idx = len(area_categories) + usage_categories.index("Residential")

    assert transformed_test[0, expected_area_idx] == 1.0
    assert transformed_test[0, expected_usage_idx] == 1.0
    assert not np.isnan(transformed_test).any()


def test_unknown_categories_in_validation_data():
    """Verify unknown categories in validation do not crash and produce zero vectors."""
    train_df = pd.DataFrame({
        "AREA_EN": ["Downtown", "Dubai Marina"],
        "USAGE_EN": ["Residential", "Commercial"],
    })
    val_df = pd.DataFrame({
        "AREA_EN": ["Unseen Area XYZ"],  # Novel unseen category
        "USAGE_EN": ["Novel Zoning ABC"], # Novel unseen category
    })

    preprocessor = build_preprocessor(
        numeric_features=[],
        categorical_features=["AREA_EN", "USAGE_EN"],
        sparse_output=False,
    )
    fit_preprocessor(preprocessor, train_df)
    transformed_val = transform_features(preprocessor, val_df)

    assert transformed_val.shape == (1, 4)
    # Both novel categories should result in an all-zeros vector
    assert np.all(transformed_val == 0.0)
    assert not np.isnan(transformed_val).any()


def test_consistent_transformed_feature_dimensions(sample_raw_data: pd.DataFrame):
    """Verify consistent column dimensions across train, validation, and test splits."""
    X_train = prepare_features(sample_raw_data.iloc[:4])
    X_val = prepare_features(sample_raw_data.iloc[4:5])
    X_test = prepare_features(sample_raw_data.iloc[5:])

    preprocessor = build_preprocessor(sparse_output=True)
    X_train_trans = fit_preprocessor(preprocessor, X_train).transform(X_train)
    X_val_trans = transform_features(preprocessor, X_val)
    X_test_trans = transform_features(preprocessor, X_test)

    assert X_train_trans.shape[0] == 4
    assert X_val_trans.shape[0] == 1
    assert X_test_trans.shape[0] == 1

    # Exact column count consistency
    assert X_train_trans.shape[1] == X_val_trans.shape[1] == X_test_trans.shape[1]


def test_no_nan_or_infinite_values_after_transformation(sample_raw_data: pd.DataFrame):
    """Verify transformed matrices contain zero NaNs and zero infinite values."""
    X_train = prepare_features(sample_raw_data.iloc[:4])
    X_test = prepare_features(sample_raw_data.iloc[4:])

    preprocessor = build_preprocessor(sparse_output=True)
    fit_preprocessor(preprocessor, X_train)

    train_trans = transform_features(preprocessor, X_train)
    test_trans = transform_features(preprocessor, X_test)

    train_metrics = check_transformed_matrix(train_trans, "Train")
    test_metrics = check_transformed_matrix(test_trans, "Test")

    assert train_metrics["nan_count"] == 0
    assert train_metrics["inf_count"] == 0
    assert test_metrics["nan_count"] == 0
    assert test_metrics["inf_count"] == 0


def test_preprocessor_fitted_only_on_training_data(sample_raw_data: pd.DataFrame):
    """Verify unfitted preprocessor raises NotFittedError and does not learn test stats."""
    preprocessor = build_preprocessor()
    X = prepare_features(sample_raw_data)

    # Transform without fit must raise NotFittedError
    with pytest.raises(NotFittedError, match="Preprocessor is not fitted"):
        transform_features(preprocessor, X)

    # Train on rows 0-3 only
    X_train = prepare_features(sample_raw_data.iloc[:4])
    X_test = prepare_features(sample_raw_data.iloc[4:])

    fit_preprocessor(preprocessor, X_train)

    # Check encoder vocabulary strictly contains categories from X_train
    cat_encoder = preprocessor.named_transformers_["categorical"].named_steps["encoder"]
    area_idx = CATEGORICAL_FEATURES.index("AREA_EN")
    learned_areas = set(cat_encoder.categories_[area_idx])

    train_areas = set(X_train["AREA_EN"].dropna().unique())
    test_areas = set(X_test["AREA_EN"].dropna().unique())

    assert learned_areas == train_areas
    # Test-only area should not be in learned vocabulary
    test_only_areas = test_areas - train_areas
    for area in test_only_areas:
        assert area not in learned_areas


def test_target_leakage_prevention(sample_raw_data: pd.DataFrame):
    """Verify rigorous prevention of target leakage across all functions."""
    # 1. prepare_features must not include TRANS_VALUE in feature columns
    with pytest.raises(ValueError, match="Target leakage prevented"):
        prepare_features(sample_raw_data, feature_cols=ALL_FEATURES + [TARGET_COLUMN])

    # 2. fit_preprocessor must raise error if TRANS_VALUE is present in X_train
    preprocessor = build_preprocessor()
    df_with_target = sample_raw_data.copy()
    with pytest.raises(ValueError, match="Target leakage detected"):
        fit_preprocessor(preprocessor, df_with_target)

    # 3. transform_features must raise error if TRANS_VALUE is present in X
    X_train = prepare_features(sample_raw_data.iloc[:4])
    fit_preprocessor(preprocessor, X_train)
    with pytest.raises(ValueError, match="Target leakage detected"):
        transform_features(preprocessor, df_with_target)


def test_identifier_leakage_prevention(sample_raw_data: pd.DataFrame):
    """Verify rigorous exclusion of TRANSACTION_NUMBER identifier."""
    # 1. prepare_features must reject TRANSACTION_NUMBER in feature_cols
    with pytest.raises(ValueError, match="Identifier leakage prevented"):
        prepare_features(sample_raw_data, feature_cols=ALL_FEATURES + [IDENTIFIER_COLUMN])

    # 2. fit_preprocessor must reject DataFrame containing TRANSACTION_NUMBER
    preprocessor = build_preprocessor()
    df_with_id = sample_raw_data[ALL_FEATURES + [IDENTIFIER_COLUMN]].copy()
    with pytest.raises(ValueError, match="Identifier leakage detected"):
        fit_preprocessor(preprocessor, df_with_id)

    # 3. transform_features must reject DataFrame containing TRANSACTION_NUMBER
    X_train = prepare_features(sample_raw_data.iloc[:4])
    fit_preprocessor(preprocessor, X_train)
    with pytest.raises(ValueError, match="Identifier leakage detected"):
        transform_features(preprocessor, df_with_id)


def test_sparse_matrix_compatibility(sample_raw_data: pd.DataFrame):
    """Verify sparse matrix output and dense fallback options."""
    X_train = prepare_features(sample_raw_data.iloc[:4])

    # Test Sparse Configuration
    sparse_preprocessor = build_preprocessor(sparse_output=True)
    fit_preprocessor(sparse_preprocessor, X_train)
    sparse_matrix = transform_features(sparse_preprocessor, X_train)

    assert sparse.issparse(sparse_matrix)
    assert hasattr(sparse_matrix, "data")
    assert hasattr(sparse_matrix, "indices")
    assert hasattr(sparse_matrix, "indptr")

    # Test Dense Configuration
    dense_preprocessor = build_preprocessor(sparse_output=False)
    fit_preprocessor(dense_preprocessor, X_train)
    dense_matrix = transform_features(dense_preprocessor, X_train)

    assert isinstance(dense_matrix, np.ndarray)
    assert not sparse.issparse(dense_matrix)
    assert sparse_matrix.shape == dense_matrix.shape


def test_fit_transform_convenience_helper(sample_raw_data: pd.DataFrame):
    """Verify fit_transform_features convenience helper produces identical output."""
    X_train = prepare_features(sample_raw_data.iloc[:4])

    prep1 = build_preprocessor()
    res1 = fit_transform_features(prep1, X_train)

    prep2 = build_preprocessor()
    fit_preprocessor(prep2, X_train)
    res2 = transform_features(prep2, X_train)

    assert (res1 != res2).nnz == 0


def test_real_approved_dataset_integration():
    """Verify pipeline executes on real approved Dubai real estate transactions."""
    from model_dataset import load_transactions

    raw_df = load_transactions()
    candidate_sales = get_candidate_sales(raw_df)

    assert len(candidate_sales) > 100000
    assert (candidate_sales["TRANS_VALUE"] > 0).all()

    # Small chronological slice for test speed
    candidate_sales["INSTANCE_DATE"] = pd.to_datetime(
        candidate_sales["INSTANCE_DATE"], errors="coerce"
    )
    sorted_sales = candidate_sales.sort_values("INSTANCE_DATE").reset_index(drop=True)

    train_slice = sorted_sales.iloc[:500].copy()
    test_slice = sorted_sales.iloc[500:600].copy()

    X_train, y_train = prepare_features(train_slice, return_target=True)
    X_test, y_test = prepare_features(test_slice, return_target=True)

    preprocessor = build_preprocessor(sparse_output=True)
    fit_preprocessor(preprocessor, X_train)

    X_train_trans = transform_features(preprocessor, X_train)
    X_test_trans = transform_features(preprocessor, X_test)

    assert sparse.issparse(X_train_trans)
    assert sparse.issparse(X_test_trans)
    assert X_train_trans.shape[1] == X_test_trans.shape[1]

    train_metrics = check_transformed_matrix(X_train_trans, "Real Train Slice")
    test_metrics = check_transformed_matrix(X_test_trans, "Real Test Slice")

    assert train_metrics["nan_count"] == 0
    assert test_metrics["nan_count"] == 0
    assert train_metrics["inf_count"] == 0
    assert test_metrics["inf_count"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
