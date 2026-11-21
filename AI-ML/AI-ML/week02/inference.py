"""
Week 2 - Day 13: Reusable Inference Module
Project: DubaiEstate AI 360 – Agentic AI-Powered Real Estate Investment
Intern: Nitesh Kumar Barnwal
Company: NEOSKILLZ
Branch: feature/week02-aiml-nitesh

Architecture & Purpose:
This module provides a production-ready, schema-validated inference function
(predict_price) that accepts a property sample (dict or DataFrame) and returns
an accurate transaction valuation point estimate in AED.

Key Capabilities:
1. Strict Schema Validation:
   - Validates input types (dict or pandas DataFrame).
   - Verifies presence of all 13 required features.
   - Detects and rejects suspicious target fields (TRANS_VALUE).
   - Handles unexpected fields gracefully or strictly.
2. Robust Value Sanitization:
   - Validates numeric features (strictly positive floats, rejects negative/zero/non-numeric).
   - Validates categorical features (handles unseen categories via handle_unknown='ignore').
3. Pipeline Caching & Persistence:
   - Loads persisted scikit-learn Pipeline artifact (candidate_pipeline.joblib).
   - Caches model in memory for sub-millisecond inference latency.
"""

from pathlib import Path
import sys
from typing import Any, Dict, List, Optional, Union

import joblib
import numpy as np
import pandas as pd

# Path configurations
CURRENT_DIR = Path(__file__).resolve().parent
DEFAULT_MODEL_PATH = CURRENT_DIR / "models" / "candidate_pipeline.joblib"

# Expected Schema Specification
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

REQUIRED_FEATURES: List[str] = NUMERIC_FEATURES + CATEGORICAL_FEATURES
DISALLOWED_FIELDS: List[str] = ["TRANS_VALUE", "TRANSACTION_NUMBER"]

# Global cache for loaded model pipeline
_CACHED_MODEL = None
_CACHED_MODEL_PATH = None


def load_model(model_path: Optional[Union[str, Path]] = None):
    """
    Load and cache the trained end-to-end model pipeline from disk.

    Parameters
    ----------
    model_path : Optional[Union[str, Path]], default None
        File path to the serialized joblib pipeline artifact.

    Returns
    -------
    sklearn.pipeline.Pipeline
        Fitted scikit-learn Pipeline containing preprocessor and regressor.

    Raises
    ------
    FileNotFoundError
        If the model artifact does not exist at the resolved path.
    """
    global _CACHED_MODEL, _CACHED_MODEL_PATH

    resolved_path = Path(model_path).resolve() if model_path else DEFAULT_MODEL_PATH.resolve()

    if _CACHED_MODEL is not None and _CACHED_MODEL_PATH == resolved_path:
        return _CACHED_MODEL

    if not resolved_path.exists():
        raise FileNotFoundError(
            f"Model pipeline artifact not found at: '{resolved_path}'. "
            "Please train the model via candidate_model.ipynb first."
        )

    pipeline = joblib.load(resolved_path)
    _CACHED_MODEL = pipeline
    _CACHED_MODEL_PATH = resolved_path
    return _CACHED_MODEL


def validate_input_schema(
    sample: Union[Dict[str, Any], pd.DataFrame],
    strict_fields: bool = False,
) -> pd.DataFrame:
    """
    Validate input sample schema, types, and values against the model specification.

    Parameters
    ----------
    sample : Dict[str, Any] or pd.DataFrame
        Property input records.
    strict_fields : bool, default False
        If True, raises ValueError when unexpected fields are present.
        If False, discards unexpected fields and retains required schema.

    Returns
    -------
    pd.DataFrame
        Validated and sanitized DataFrame formatted for the model pipeline.

    Raises
    ------
    TypeError
        If sample is not a dictionary or pandas DataFrame.
    ValueError
        If required features are missing, disallowed target fields are present,
        numeric fields are negative/non-numeric, or input is malformed.
    """
    # 1. Type validation
    if isinstance(sample, dict):
        df = pd.DataFrame([sample])
    elif isinstance(sample, pd.DataFrame):
        df = sample.copy()
    else:
        raise TypeError(
            f"Input sample must be a dict or pandas DataFrame, got {type(sample).__name__}."
        )

    if df.empty:
        raise ValueError("Input sample is empty. At least one property record must be provided.")

    # 2. Check for target or identifier leakage
    for field in DISALLOWED_FIELDS:
        if field in df.columns:
            raise ValueError(
                f"Disallowed field '{field}' detected in input! "
                "Target values and identifiers must not be provided at inference time."
            )

    # 3. Check for missing required features
    missing_features = [f for f in REQUIRED_FEATURES if f not in df.columns]
    if missing_features:
        raise ValueError(
            f"Missing required feature(s): {missing_features}. "
            f"All {len(REQUIRED_FEATURES)} features must be provided: {REQUIRED_FEATURES}"
        )

    # 4. Check for unexpected fields
    unexpected_fields = [c for c in df.columns if c not in REQUIRED_FEATURES]
    if unexpected_fields:
        if strict_fields:
            raise ValueError(
                f"Unexpected field(s) detected in input: {unexpected_fields}. "
                f"Allowed features are: {REQUIRED_FEATURES}"
            )
        # Discard unexpected fields and retain exact required feature order
        df = df[REQUIRED_FEATURES].copy()
    else:
        df = df[REQUIRED_FEATURES].copy()

    # 5. Validate numeric features
    for col in NUMERIC_FEATURES:
        # Convert to numeric, raising error on unconvertible values
        numeric_series = pd.to_numeric(df[col], errors="coerce")
        if numeric_series.isna().any():
            # Check if original was null or unparseable
            null_mask = df[col].isna()
            if not null_mask.all() and numeric_series.isna().sum() > null_mask.sum():
                invalid_val = df[col].loc[~null_mask & numeric_series.isna()].iloc[0]
                raise ValueError(
                    f"Invalid numeric value for '{col}': '{invalid_val}'. "
                    "Must be a valid real number."
                )

        # Check for non-positive values
        invalid_positives = numeric_series[numeric_series <= 0]
        if not invalid_positives.empty:
            raise ValueError(
                f"Invalid value for '{col}': {invalid_positives.iloc[0]}. "
                "Property area dimensions must be strictly positive (> 0)."
            )

        df[col] = numeric_series

    # 6. Validate categorical features
    for col in CATEGORICAL_FEATURES:
        # Standardize strings, convert non-null to str
        df[col] = df[col].apply(
            lambda x: str(x).strip() if pd.notna(x) and not isinstance(x, (dict, list, set)) else (x if pd.notna(x) else np.nan)
        )
        # Check for unhashable nested types
        for val in df[col]:
            if isinstance(val, (dict, list, set)):
                raise ValueError(f"Invalid categorical value for '{col}': {val}. Must be a string or scalar.")

    return df


def predict_price(
    sample: Union[Dict[str, Any], pd.DataFrame],
    model_path: Optional[Union[str, Path]] = None,
    strict_fields: bool = False,
) -> Union[float, List[float]]:
    """
    Predict property transaction market valuation in United Arab Emirates Dirham (AED).

    Parameters
    ----------
    sample : Dict[str, Any] or pd.DataFrame
        Single property record dictionary or batch DataFrame containing required features.
    model_path : Optional[Union[str, Path]], default None
        Optional path to a custom model pipeline artifact.
    strict_fields : bool, default False
        Whether to reject extra unexpected fields.

    Returns
    -------
    float or List[float]
        Point estimate transaction valuation in AED.
        Returns float if input was a single-record dict or 1-row DataFrame.
        Returns list of floats if input was a multi-row DataFrame.

    Raises
    ------
    TypeError
        If sample is not a dictionary or pandas DataFrame.
    ValueError
        If validation fails on schema, missing fields, or invalid numeric values.
    """
    validated_df = validate_input_schema(sample, strict_fields=strict_fields)
    pipeline = load_model(model_path=model_path)

    predictions = pipeline.predict(validated_df)

    # Sanity checks on output
    if not np.isfinite(predictions).all():
        raise RuntimeError("Model produced non-finite prediction values.")

    if isinstance(sample, dict) or len(validated_df) == 1:
        return float(round(predictions[0], 2))

    return [float(round(p, 2)) for p in predictions]


if __name__ == "__main__":
    print("=" * 65)
    print("DAY 13 INFERENCE SMOKE TEST")
    print("=" * 65)

    sample_property = {
        "PROCEDURE_AREA": 125.5,
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

    try:
        valuation = predict_price(sample_property)
        print(f"Sample Input Property: 2 B/R Flat in JVC (120 sqm)")
        print(f"Predicted Valuation:   AED {valuation:,.2f}")
        print("Inference test passed successfully!")
    except Exception as e:
        print(f"Inference test failed: {e}")
