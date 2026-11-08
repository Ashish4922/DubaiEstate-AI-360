
import re
from datetime import date

import pandas as pd

from Genai.report import build_report


def make_df() -> pd.DataFrame:
    rows = []
    for area, base in (("Area A", 100), ("Area B", 200), ("Area C", 300)):
        for i in range(35):  # above the 30-row minimum sample
            rows.append((area, f"T-{area[-1]}-{i}", base + i))
    return pd.DataFrame(
        {
            "TRANSACTION_NUMBER": [r[1] for r in rows],
            "GROUP_EN": "Sales",
            "INSTANCE_DATE": pd.to_datetime("2026-01-15"),
            "IS_OFFPLAN_EN": "Ready",
            "AREA_EN": [r[0] for r in rows],
            "PROP_TYPE_EN": "Unit",
            "PROP_SB_TYPE_EN": "Flat",
            "TRANS_VALUE": [r[2] for r in rows],
            "ACTUAL_AREA": 10,
        }
    )


def make_audit(df: pd.DataFrame) -> dict:
    return {
        "rows_loaded": len(df),
        "exact_duplicates_removed": 0,
        "duplicate_keys_with_different_data": 0,
        "invalid_rows_removed": 0,
        "rows_final": len(df),
        "date_start": df["INSTANCE_DATE"].min(),
        "date_end": df["INSTANCE_DATE"].max(),
    }


def report() -> str:
    df = make_df()
    return build_report(df, make_audit(df), today=date(2026, 11, 6))


def test_report_is_marked_as_draft():
    assert "(DRAFT)" in report()


def test_every_reference_used_is_defined_in_sources():
    text = report()
    used = set(re.findall(r"\[([AR]\d+)\]", text))
    defined = set(re.findall(r"^\| ([AR]\d+) \|", text, flags=re.MULTILINE))
    assert used, "the report should contain citations"
    assert used <= defined


def test_row_count_in_report_matches_the_data():
    df = make_df()
    assert f"{len(df):,}" in build_report(df, make_audit(df))


def test_partial_month_is_labelled():
    assert "partial" in report().lower()


def test_report_contains_no_forward_looking_language():
    text = report().lower()
    for phrase in ("forecast", "predict", "guarantee", "will rise", "will increase", "expected to"):
        assert phrase not in text


def test_disclaimer_is_present():
    assert "not investment advice" in report()


def test_report_is_repeatable():
    assert report() == report()