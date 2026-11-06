
import pandas as pd

from Genai.retrieval import (
    median_price_per_sqm,
    median_sale_value,
    top_areas_by_count,
)


def make_df() -> pd.DataFrame:
    rows = [
        # area, prop_type, subtype, value, size
        ("Area A", "Unit", "Flat", 100, 10),
        ("Area A", "Unit", "Flat", 200, 10),
        ("Area A", "Unit", "Flat", 300, 10),
        ("Area B", "Land", "Land", 5000, 100),
    ]
    return pd.DataFrame(
        {
            "GROUP_EN": "Sales",
            "INSTANCE_DATE": pd.to_datetime("2026-01-15"),
            "IS_OFFPLAN_EN": "Ready",
            "AREA_EN": [r[0] for r in rows],
            "PROP_TYPE_EN": [r[1] for r in rows],
            "PROP_SB_TYPE_EN": [r[2] for r in rows],
            "TRANS_VALUE": [r[3] for r in rows],
            "ACTUAL_AREA": [r[4] for r in rows],
        }
    )


def test_median_value_matches_hand_calculation():
    result = median_sale_value(make_df(), area="area a", subtype="Flat")
    assert result["value"] == 200
    assert result["sample_size"] == 3


def test_small_sample_is_flagged():
    result = median_sale_value(make_df(), area="Area A")
    assert "not reliable" in result["warnings"]


def test_unknown_area_returns_no_value():
    result = median_sale_value(make_df(), area="Atlantis")
    assert result["value"] is None
    assert "not found" in result["warnings"]


def test_price_per_sqm_excludes_land():
    result = median_price_per_sqm(make_df())
    assert result["value"] == 20  # units only: 10, 20, 30 AED per sq m
    assert result["sample_size"] == 3


def test_top_areas_counts_rows():
    result = top_areas_by_count(make_df(), n=1)
    assert result["value"] == {"Area A": 3}