"""
Unit and Integration Tests for Week 2 Day 13 Reusable Inference Module.
Project: DubaiEstate AI 360 – Agentic AI-Powered Real Estate Investment
Intern: Nitesh Kumar Barnwal
Branch: feature/week02-aiml-nitesh

Coverage:
1. Valid synthetic input prediction (dict and DataFrame).
2. Missing required feature validation.
3. Unexpected field handling (lenient and strict mode).
4. Prevention of target / identifier input (TRANS_VALUE, TRANSACTION_NUMBER).
5. Invalid numeric value rejection (negative, zero, non-numeric strings).
6. Handling novel / unseen categorical values without crashing.
7. Incorrect input type rejection (TypeError for invalid types).
8. Empty sample validation.
9. Verification of finite, strictly positive output.
10. Model persistence and reload reproducibility.
"""

from pathlib import Path
import sys
from typing import Dict, Any

import numpy as np
import pandas as pd
import pytest

# Ensure week02 directory is available in sys.path
WEEK02_DIR = Path(__file__).resolve().parents[1]
if str(WEEK02_DIR) not in sys.path:
    sys.path.insert(0, str(WEEK02_DIR))

from inference import (
    DEFAULT_MODEL_PATH,
    REQUIRED_FEATURES,
    load_model,
    predict_price,
    validate_input_schema,
)


@pytest.fixture
def valid_property_dict() -> Dict[str, Any]:
    """Fixture providing a valid 2 B/R apartment record in Dubai."""
    return {
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


def test_predict_price_valid_dict(valid_property_dict: Dict[str, Any]):
    """Verify inference returns a positive finite float for a valid property dict."""
    price = predict_price(valid_property_dict)

    assert isinstance(price, float)
    assert np.isfinite(price)
    assert price > 0
    assert price > 100_000  # Reasonable real estate price lower bound


def test_predict_price_valid_dataframe(valid_property_dict: Dict[str, Any]):
    """Verify inference accepts a multi-row DataFrame and returns a list of floats."""
    df_input = pd.DataFrame([valid_property_dict, valid_property_dict])
    predictions = predict_price(df_input)

    assert isinstance(predictions, list)
    assert len(predictions) == 2
    assert all(isinstance(p, float) for p in predictions)
    assert all(np.isfinite(p) for p in predictions)
    assert predictions[0] == predictions[1]


def test_missing_required_fields(valid_property_dict: Dict[str, Any]):
    """Verify ValueError is raised when required features are omitted."""
    # 1. Missing numeric field
    missing_area = valid_property_dict.copy()
    del missing_area["ACTUAL_AREA"]
    with pytest.raises(ValueError, match="Missing required feature"):
        predict_price(missing_area)

    # 2. Missing categorical field
    missing_area_name = valid_property_dict.copy()
    del missing_area_name["AREA_EN"]
    with pytest.raises(ValueError, match="Missing required feature"):
        predict_price(missing_area_name)


def test_unexpected_fields_handling(valid_property_dict: Dict[str, Any]):
    """Verify unexpected fields are discarded in default mode and rejected in strict mode."""
    sample_with_extra = valid_property_dict.copy()
    sample_with_extra["UNEXPECTED_COLUMN_XYZ"] = "Extra Data"

    # Default lenient mode: should filter unexpected column and succeed
    price = predict_price(sample_with_extra, strict_fields=False)
    assert isinstance(price, float)
    assert price > 0

    # Strict mode: should raise ValueError
    with pytest.raises(ValueError, match="Unexpected field"):
        predict_price(sample_with_extra, strict_fields=True)


def test_disallowed_target_leakage_field(valid_property_dict: Dict[str, Any]):
    """Verify ValueError is raised if TRANS_VALUE or TRANSACTION_NUMBER is provided."""
    # Target leakage check
    sample_with_target = valid_property_dict.copy()
    sample_with_target["TRANS_VALUE"] = 1500000.0
    with pytest.raises(ValueError, match="Disallowed field 'TRANS_VALUE'"):
        predict_price(sample_with_target)

    # Identifier check
    sample_with_id = valid_property_dict.copy()
    sample_with_id["TRANSACTION_NUMBER"] = "TX-99999"
    with pytest.raises(ValueError, match="Disallowed field 'TRANSACTION_NUMBER'"):
        predict_price(sample_with_id)


def test_invalid_numeric_values(valid_property_dict: Dict[str, Any]):
    """Verify invalid numeric values (negative, zero, unparseable) are rejected."""
    # Negative area
    neg_sample = valid_property_dict.copy()
    neg_sample["ACTUAL_AREA"] = -50.0
    with pytest.raises(ValueError, match="strictly positive"):
        predict_price(neg_sample)

    # Zero area
    zero_sample = valid_property_dict.copy()
    zero_sample["PROCEDURE_AREA"] = 0.0
    with pytest.raises(ValueError, match="strictly positive"):
        predict_price(zero_sample)

    # Non-numeric string
    str_sample = valid_property_dict.copy()
    str_sample["ACTUAL_AREA"] = "not_a_number"
    with pytest.raises(ValueError, match="Invalid numeric value"):
        predict_price(str_sample)


def test_unseen_categorical_values(valid_property_dict: Dict[str, Any]):
    """Verify unseen / novel categories do not crash and produce valid finite estimates."""
    unseen_sample = valid_property_dict.copy()
    unseen_sample["AREA_EN"] = "Completely Novel District 99"
    unseen_sample["NEAREST_METRO_EN"] = "Hyperloop Station Alpha"
    unseen_sample["PROP_SB_TYPE_EN"] = "Futuristic Pod"

    price = predict_price(unseen_sample)
    assert isinstance(price, float)
    assert np.isfinite(price)
    assert price > 0


def test_invalid_input_types():
    """Verify TypeError is raised when input is not a dict or DataFrame."""
    with pytest.raises(TypeError, match="must be a dict or pandas DataFrame"):
        predict_price("Just a string")  # type: ignore

    with pytest.raises(TypeError, match="must be a dict or pandas DataFrame"):
        predict_price([1, 2, 3])  # type: ignore

    with pytest.raises(TypeError, match="must be a dict or pandas DataFrame"):
        predict_price(42)  # type: ignore


def test_empty_input():
    """Verify ValueError is raised on empty dict or DataFrame."""
    with pytest.raises(ValueError, match="Input sample is empty"):
        predict_price({})

    with pytest.raises(ValueError, match="Input sample is empty"):
        predict_price(pd.DataFrame())


def test_model_persistence_and_reload(valid_property_dict: Dict[str, Any]):
    """Verify the saved joblib model can be loaded from disk and produces identical predictions."""
    assert DEFAULT_MODEL_PATH.exists()

    model1 = load_model(DEFAULT_MODEL_PATH)
    model2 = load_model(DEFAULT_MODEL_PATH)
    assert model1 is model2  # In-memory caching verification

    pred1 = predict_price(valid_property_dict, model_path=DEFAULT_MODEL_PATH)
    pred2 = predict_price(valid_property_dict, model_path=DEFAULT_MODEL_PATH)
    assert pred1 == pred2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
