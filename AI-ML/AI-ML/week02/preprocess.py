"""
Week 2 - Day 9: Preprocessing Pipeline
Project: DubaiEstate AI 360 – Agentic AI-Powered Real Estate Investment
Intern: Nitesh Kumar Barnwal
Company: NEOSKILLZ
Branch: feature/week02-aiml-nitesh

Architecture & Purpose:
This module implements a reusable, modular, and leakage-free scikit-learn
preprocessing pipeline for predicting Dubai real estate transaction values (TRANS_VALUE).

Key Pipeline Features:
1. Numeric Pipeline:
   - Median imputation (SimpleImputer(strategy='median')) for missing area values.
   - StandardScaler() for zero mean and unit variance.
2. Categorical Pipeline:
   - Most-frequent imputation (SimpleImputer(strategy='most_frequent')).
   - OneHotEncoder(handle_unknown='ignore', sparse_output=True) for high-cardinality features.
3. Data Leakage Prevention:
   - Pipeline parameters (medians, scalers, category vocabularies) fitted strictly on training split.
   - Prediction target (TRANS_VALUE) and identifiers (TRANSACTION_NUMBER) strictly excluded.
   - Validation and test splits transformed using frozen preprocessor.
4. Memory Efficiency:
   - Preserves sparse CSR matrix output (scipy.sparse.csr_matrix) to prevent memory allocation errors.
"""

from pathlib import Path
import sys
from typing import List, Optional, Tuple, Union, Dict, Any

import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.compose import ColumnTransformer
from sklearn.exceptions import NotFittedError
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.utils.validation import check_is_fitted

# Ensure week02 directory is on sys.path for local module resolution
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

# Target and Identifier definitions
TARGET_COLUMN: str = "TRANS_VALUE"
IDENTIFIER_COLUMN: str = "TRANSACTION_NUMBER"
DATE_COLUMN: str = "INSTANCE_DATE"

# Permitted Feature Whitelist (aligned with Day 8 analysis)
NUMERIC_FEATURES: List[str] = [
    "PROCEDURE_AREA",
    "ACTUAL_AREA",
]

CATEGORICAL_FEATURES: List[str] = [
    "PROCEDURE_EN",
    "IS_OFFPLAN_EN",
    "IS_FREE_HOLD_EN",
    "USAGE_EN",
    "AREA_EN",
    "PROP_TYPE_EN",
    "PROP_SB_TYPE_EN",
    "ROOMS_EN",
    "NEAREST_METRO_EN",
    "NEAREST_MALL_EN",
    "NEAREST_LANDMARK_EN",
]

ALL_FEATURES: List[str] = NUMERIC_FEATURES + CATEGORICAL_FEATURES

# Explicit Exclusions & Leakage Safeguards
EXCLUDED_COLUMNS: List[str] = [
    TARGET_COLUMN,         # Continuous target variable (target leakage)
    IDENTIFIER_COLUMN,     # Arbitrary post-registration ID (memorization leakage)
    DATE_COLUMN,           # Temporal metadata for chronological splitting
    "GROUP_EN",            # Constant 'Sales' (zero variance)
    "TOTAL_BUYER",         # Constant 0 across transactions (post-hoc administrative counter)
    "TOTAL_SELLER",        # Constant 0 across transactions (post-hoc administrative counter)
    "MASTER_PROJECT_EN",   # ~99.6% missing values (extreme sparsity)
    "PROJECT_EN",          # High cardinality (2,968+ categories; causes variance inflation)
    "PARKING",             # Inconsistent mixed text format; excluded from baseline
]


def get_candidate_sales(df: pd.DataFrame) -> pd.DataFrame:
    """
    Isolate candidate arm's-length sale transactions from raw transactions.

    Reuses Day 8 procedure analysis logic from model_dataset.py:
    - Filters PROCEDURE_EN matching 'sell' or 'sale' (case-insensitive regex).
    - Enforces strictly positive target values (TRANS_VALUE > 0).
    - Drops zero or negative target records.

    Parameters
    ----------
    df : pd.DataFrame
        Raw transactions dataframe loaded from CSV files.

    Returns
    -------
    pd.DataFrame
        Filtered candidate sale records.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Input must be a pandas DataFrame, got {type(df).__name__}.")

    if "PROCEDURE_EN" not in df.columns:
        raise ValueError("Required column 'PROCEDURE_EN' not found in DataFrame.")

    sale_mask = (
        df["PROCEDURE_EN"]
        .astype("string")
        .str.contains(r"\bsell\b|\bsale\b", case=False, na=False)
    )

    eligible = df.loc[sale_mask].copy()

    if TARGET_COLUMN in eligible.columns:
        target_series = pd.to_numeric(eligible[TARGET_COLUMN], errors="coerce")
        eligible = eligible.loc[target_series.gt(0)].copy()

    return eligible


def prepare_features(
    df: pd.DataFrame,
    feature_cols: Optional[List[str]] = None,
    target_col: str = TARGET_COLUMN,
    return_target: bool = False,
) -> Union[pd.DataFrame, Tuple[pd.DataFrame, pd.Series]]:
    """
    Extract and validate model feature matrix from transaction data,
    strictly preventing target and identifier data leakage.

    Parameters
    ----------
    df : pd.DataFrame
        Input transaction records.
    feature_cols : Optional[List[str]], default None
        List of feature column names to extract. Defaults to ALL_FEATURES.
    target_col : str, default 'TRANS_VALUE'
        Name of the prediction target variable.
    return_target : bool, default False
        If True, returns tuple (X, y).
        If False, returns feature DataFrame X only.

    Returns
    -------
    pd.DataFrame or Tuple[pd.DataFrame, pd.Series]
        Feature DataFrame X (or tuple of X and target Series y if return_target=True).

    Raises
    ------
    TypeError
        If df is not a pandas DataFrame.
    ValueError
        If target_col or TRANSACTION_NUMBER is included in feature_cols,
        or if required feature columns are missing from df.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Input must be a pandas DataFrame, got {type(df).__name__}.")

    cols = list(feature_cols) if feature_cols is not None else list(ALL_FEATURES)

    # Prevent target leakage
    if target_col in cols:
        raise ValueError(
            f"Target leakage prevented: Target column '{target_col}' cannot be included "
            "in input features."
        )

    # Prevent identifier leakage
    if IDENTIFIER_COLUMN in cols:
        raise ValueError(
            f"Identifier leakage prevented: Column '{IDENTIFIER_COLUMN}' must not be "
            "included in model features."
        )

    # Ensure required feature columns exist in df
    missing_cols = [col for col in cols if col not in df.columns]
    if missing_cols:
        raise ValueError(
            f"Missing required feature columns in input DataFrame: {missing_cols}"
        )

    # Extract feature matrix and standardize missing value representations
    X = df[cols].copy().fillna(np.nan)

    # Safety assertion: guarantee no target or identifier leakage
    if target_col in X.columns:
        raise ValueError(f"Target column '{target_col}' detected in feature matrix X!")
    if IDENTIFIER_COLUMN in X.columns:
        raise ValueError(f"Identifier column '{IDENTIFIER_COLUMN}' detected in feature matrix X!")

    if return_target:
        if target_col not in df.columns:
            raise KeyError(
                f"Target column '{target_col}' requested but not found in input DataFrame."
            )
        y = pd.to_numeric(df[target_col], errors="coerce")
        return X, y

    return X


def build_preprocessor(
    numeric_features: Optional[List[str]] = None,
    categorical_features: Optional[List[str]] = None,
    scale_numeric: bool = True,
    sparse_output: bool = True,
) -> ColumnTransformer:
    """
    Construct a reusable, leakage-free scikit-learn ColumnTransformer.

    Architecture:
    - Numeric pipeline:
        1. SimpleImputer(strategy='median') for handling missing area values.
        2. StandardScaler() (optional, enabled by default) for zero mean, unit variance.
    - Categorical pipeline:
        1. SimpleImputer(strategy='most_frequent') for handling missing categories.
        2. OneHotEncoder(handle_unknown='ignore', sparse_output=sparse_output)
           to gracefully handle novel categories in validation/test splits.

    Parameters
    ----------
    numeric_features : Optional[List[str]], default None
        List of numeric feature column names. Defaults to NUMERIC_FEATURES.
    categorical_features : Optional[List[str]], default None
        List of categorical feature column names. Defaults to CATEGORICAL_FEATURES.
    scale_numeric : bool, default True
        Whether to apply StandardScaler to numeric features.
    sparse_output : bool, default True
        Whether to produce a sparse CSR matrix. Recommended True for high-cardinality
        categorical data to avoid multi-gigabyte memory exhaustion.

    Returns
    -------
    ColumnTransformer
        Unfitted scikit-learn ColumnTransformer instance.
    """
    num_cols = (
        list(numeric_features)
        if numeric_features is not None
        else list(NUMERIC_FEATURES)
    )
    cat_cols = (
        list(categorical_features)
        if categorical_features is not None
        else list(CATEGORICAL_FEATURES)
    )

    num_steps = [("imputer", SimpleImputer(strategy="median"))]
    if scale_numeric:
        num_steps.append(("scaler", StandardScaler()))
    numeric_pipeline = Pipeline(steps=num_steps)

    cat_steps = [
        ("imputer", SimpleImputer(strategy="most_frequent")),
        (
            "encoder",
            OneHotEncoder(
                handle_unknown="ignore",
                sparse_output=sparse_output,
            ),
        ),
    ]
    categorical_pipeline = Pipeline(steps=cat_steps)

    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, num_cols),
            ("categorical", categorical_pipeline, cat_cols),
        ],
        remainder="drop",
        sparse_threshold=1.0 if sparse_output else 0.0,
        verbose_feature_names_out=False,
    )

    return preprocessor


def fit_preprocessor(
    preprocessor: ColumnTransformer,
    X_train: pd.DataFrame,
    target_col: str = TARGET_COLUMN,
) -> ColumnTransformer:
    """
    Fit preprocessor strictly on training features.

    Enforces strict data leakage safeguards:
    - Asserts that target_col is NOT present in X_train.
    - Asserts that TRANSACTION_NUMBER is NOT present in X_train.
    - Ensures statistics (medians, means, stds, one-hot vocabularies) are learned
      exclusively from training transactions.

    Parameters
    ----------
    preprocessor : ColumnTransformer
        Unfitted ColumnTransformer instance.
    X_train : pd.DataFrame
        Training feature DataFrame.
    target_col : str, default 'TRANS_VALUE'
        Target variable name to check for leakage prevention.

    Returns
    -------
    ColumnTransformer
        Fitted ColumnTransformer instance.

    Raises
    ------
    TypeError
        If preprocessor or X_train is not of expected type.
    ValueError
        If target_col or TRANSACTION_NUMBER is present in X_train.
    """
    if not isinstance(preprocessor, ColumnTransformer):
        raise TypeError(
            f"preprocessor must be a ColumnTransformer, got {type(preprocessor).__name__}."
        )
    if not isinstance(X_train, pd.DataFrame):
        raise TypeError(
            f"X_train must be a pandas DataFrame, got {type(X_train).__name__}."
        )

    if target_col in X_train.columns:
        raise ValueError(
            f"Target leakage detected: Target variable '{target_col}' found in training "
            "feature matrix! Preprocessing must never be fitted on target values."
        )

    if IDENTIFIER_COLUMN in X_train.columns:
        raise ValueError(
            f"Identifier leakage detected: Identifier '{IDENTIFIER_COLUMN}' found in "
            "training feature matrix! Exclude identifiers before fitting."
        )

    X_train_clean = X_train.fillna(np.nan)
    preprocessor.fit(X_train_clean)
    return preprocessor


def transform_features(
    preprocessor: ColumnTransformer,
    X: pd.DataFrame,
    target_col: str = TARGET_COLUMN,
) -> Union[sparse.spmatrix, np.ndarray]:
    """
    Transform evaluation or test feature matrix using a pre-fitted preprocessor.

    Enforces strict data leakage safeguards:
    - Asserts that preprocessor has already been fitted on training data.
    - Asserts that target_col is NOT present in X.
    - Asserts that TRANSACTION_NUMBER is NOT present in X.
    - Does NOT refit or modify preprocessor parameters.

    Parameters
    ----------
    preprocessor : ColumnTransformer
        Fitted ColumnTransformer instance.
    X : pd.DataFrame
        Feature DataFrame to transform.
    target_col : str, default 'TRANS_VALUE'
        Target variable name to check for leakage prevention.

    Returns
    -------
    scipy.sparse.spmatrix or np.ndarray
        Transformed feature matrix.

    Raises
    ------
    TypeError
        If preprocessor or X is not of expected type.
    NotFittedError
        If preprocessor has not been fitted prior to transformation.
    ValueError
        If target_col or TRANSACTION_NUMBER is present in X.
    """
    if not isinstance(preprocessor, ColumnTransformer):
        raise TypeError(
            f"preprocessor must be a ColumnTransformer, got {type(preprocessor).__name__}."
        )
    if not isinstance(X, pd.DataFrame):
        raise TypeError(
            f"X must be a pandas DataFrame, got {type(X).__name__}."
        )

    try:
        check_is_fitted(preprocessor)
    except NotFittedError:
        raise NotFittedError(
            "Preprocessor is not fitted! Preprocessor must be fitted strictly on training data "
            "via fit_preprocessor() before transforming validation or test features."
        )

    if target_col in X.columns:
        raise ValueError(
            f"Target leakage detected: Target variable '{target_col}' found in feature "
            "matrix to transform! Never transform feature matrices containing the target."
        )

    if IDENTIFIER_COLUMN in X.columns:
        raise ValueError(
            f"Identifier leakage detected: Identifier '{IDENTIFIER_COLUMN}' found in "
            "feature matrix to transform! Exclude identifiers before transforming."
        )

    X_clean = X.fillna(np.nan)
    return preprocessor.transform(X_clean)


def fit_transform_features(
    preprocessor: ColumnTransformer,
    X_train: pd.DataFrame,
    target_col: str = TARGET_COLUMN,
) -> Union[sparse.spmatrix, np.ndarray]:
    """
    Convenience function to fit preprocessor strictly on training features
    and return transformed training matrix.

    Parameters
    ----------
    preprocessor : ColumnTransformer
        ColumnTransformer instance to fit.
    X_train : pd.DataFrame
        Training feature DataFrame.
    target_col : str, default 'TRANS_VALUE'
        Target variable name to check for leakage prevention.

    Returns
    -------
    scipy.sparse.spmatrix or np.ndarray
        Transformed training feature matrix.
    """
    fitted_preprocessor = fit_preprocessor(preprocessor, X_train, target_col=target_col)
    return transform_features(fitted_preprocessor, X_train, target_col=target_col)


def check_transformed_matrix(
    matrix: Union[sparse.spmatrix, np.ndarray],
    name: str = "Transformed matrix",
) -> Dict[str, Any]:
    """
    Validate numerical integrity of a transformed feature matrix (sparse or dense).

    Verifies:
    - Zero NaN values.
    - Zero infinite values.
    - Matrix dimensions and density.

    Parameters
    ----------
    matrix : scipy.sparse.spmatrix or np.ndarray
        Transformed feature matrix to inspect.
    name : str, default 'Transformed matrix'
        Descriptive label for error logging.

    Returns
    -------
    Dict[str, Any]
        Dictionary of validation metrics.

    Raises
    ------
    ValueError
        If NaN or infinite entries are detected.
    """
    is_sparse = sparse.issparse(matrix)

    if is_sparse:
        values = matrix.data
    else:
        values = np.asarray(matrix).ravel()

    nan_count = int(np.isnan(values).sum())
    inf_count = int(np.isinf(values).sum())

    if nan_count > 0:
        raise ValueError(f"{name} contains {nan_count} NaN values after transformation.")
    if inf_count > 0:
        raise ValueError(f"{name} contains {inf_count} infinite values after transformation.")

    return {
        "name": name,
        "shape": matrix.shape,
        "is_sparse": is_sparse,
        "nan_count": nan_count,
        "inf_count": inf_count,
        "is_valid": True,
    }


def main():
    """
    Execute full end-to-end preprocessing demonstration using real Dubai transactions dataset.
    Follows strict 70/15/15 chronological train/val/test splitting without lookahead bias.
    """
    from model_dataset import load_transactions

    print("=" * 70)
    print("WEEK 2 - DAY 9: PREPROCESSING PIPELINE EXECUTION")
    print("=" * 70)

    # 1. Load full raw dataset using Day 8 loader
    print("\n[Step 1] Loading transactions from CSV source files...")
    raw_df = load_transactions()
    print(f"Loaded raw records: {len(raw_df):,} rows, {raw_df.shape[1]} columns")

    # 2. Filter candidate sales using Day 8 logic
    print("\n[Step 2] Isolating arm's-length candidate sales...")
    sales_df = get_candidate_sales(raw_df)
    print(f"Eligible sales records: {len(sales_df):,} rows")

    # 3. Chronological sorting by INSTANCE_DATE
    print("\n[Step 3] Chronological sorting for temporal split (no lookahead bias)...")
    sales_df["INSTANCE_DATE"] = pd.to_datetime(
        sales_df["INSTANCE_DATE"], errors="coerce"
    )
    sales_df = sales_df.sort_values("INSTANCE_DATE").reset_index(drop=True)

    # 4. Strict 70% / 15% / 15% train/val/test split
    n = len(sales_df)
    n_train = int(n * 0.70)
    n_val = int(n * 0.15)

    train_data = sales_df.iloc[:n_train].copy()
    val_data = sales_df.iloc[n_train : n_train + n_val].copy()
    test_data = sales_df.iloc[n_train + n_val :].copy()

    print(f"Training split   (70%): {len(train_data):,} records")
    print(f"Validation split (15%): {len(val_data):,} records")
    print(f"Test split       (15%): {len(test_data):,} records")

    # 5. Prepare feature matrices (target leakage prevented)
    print("\n[Step 4] Extracting feature matrices (prepare_features)...")
    X_train, y_train = prepare_features(train_data, return_target=True)
    X_val, y_val = prepare_features(val_data, return_target=True)
    X_test, y_test = prepare_features(test_data, return_target=True)

    print(f"X_train features shape: {X_train.shape}")
    print(f"Target column in X_train? {TARGET_COLUMN in X_train.columns}")
    print(f"Identifier column in X_train? {IDENTIFIER_COLUMN in X_train.columns}")

    # 6. Build preprocessor
    print("\n[Step 5] Building scikit-learn ColumnTransformer...")
    preprocessor = build_preprocessor(sparse_output=True)
    print(f"Numeric features ({len(NUMERIC_FEATURES)}): {NUMERIC_FEATURES}")
    print(f"Categorical features ({len(CATEGORICAL_FEATURES)}): {CATEGORICAL_FEATURES}")

    # 7. Fit preprocessor strictly on training data
    print("\n[Step 6] Fitting preprocessor STRICTLY on X_train...")
    fit_preprocessor(preprocessor, X_train)
    print("Preprocessor successfully fitted on training split exclusively.")

    # 8. Transform splits
    print("\n[Step 7] Transforming feature splits...")
    X_train_trans = transform_features(preprocessor, X_train)
    X_val_trans = transform_features(preprocessor, X_val)
    X_test_trans = transform_features(preprocessor, X_test)

    # 9. Numerical integrity verification
    print("\n[Step 8] Verifying transformed matrix integrity...")
    train_check = check_transformed_matrix(X_train_trans, "Training Matrix")
    val_check = check_transformed_matrix(X_val_trans, "Validation Matrix")
    test_check = check_transformed_matrix(X_test_trans, "Test Matrix")

    print(f"Train matrix shape: {train_check['shape']} | Sparse: {train_check['is_sparse']} | NaNs: {train_check['nan_count']}")
    print(f"Val matrix shape:   {val_check['shape']} | Sparse: {val_check['is_sparse']} | NaNs: {val_check['nan_count']}")
    print(f"Test matrix shape:  {test_check['shape']} | Sparse: {test_check['is_sparse']} | NaNs: {test_check['nan_count']}")

    assert X_train_trans.shape[1] == X_val_trans.shape[1] == X_test_trans.shape[1], (
        "Feature column dimensions do not match across splits!"
    )

    print("\n" + "=" * 70)
    print("DAY 9 PREPROCESSING PIPELINE VALIDATION COMPLETED SUCCESSFULLY")
    print("=" * 70)


if __name__ == "__main__":
    main()
