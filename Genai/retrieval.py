from __future__ import annotations

import difflib
import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

DATA_DIR = Path("DataSets")
PART_FILES = (
    "dubai_transactions_2026_part_1.csv",
    "dubai_transactions_2026_part_2.csv",
)
REQUIRED_COLUMNS = (
    "TRANSACTION_NUMBER",
    "INSTANCE_DATE",
    "GROUP_EN",
    "IS_OFFPLAN_EN",
    "AREA_EN",
    "PROP_TYPE_EN",
    "PROP_SB_TYPE_EN",
    "TRANS_VALUE",
    "ACTUAL_AREA",
)

# Project convention, not a statistical guarantee.
MIN_SAMPLE_SIZE = 30

# Loading and auditing

def load_transactions(data_dir: Path | str = DATA_DIR) -> tuple[pd.DataFrame, dict]:
    """Load both CSV parts, validate them and return (dataframe, audit).

    Raises FileNotFoundError if a part is missing and ValueError if the
    headers differ or a required column is absent.
    """
    frames = []
    for name in PART_FILES:
        path = Path(data_dir) / name
        if not path.exists():
            raise FileNotFoundError(f"Dataset file not found: {path}")
        frames.append(pd.read_csv(path, low_memory=False))

    columns = list(frames[0].columns)
    for frame in frames[1:]:
        if list(frame.columns) != columns:
            raise ValueError("The CSV parts do not have identical headers.")

    missing = [c for c in REQUIRED_COLUMNS if c not in columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    df = pd.concat(frames, ignore_index=True)
    rows_loaded = len(df)

    # Exact full-row copies are safe to drop. Rows that share a transaction
    # number but differ elsewhere are kept and only reported.
    exact_duplicates = int(df.duplicated(keep="first").sum())
    df = df.drop_duplicates(keep="first")
    duplicate_keys_left = int(df["TRANSACTION_NUMBER"].duplicated().sum())

    df["INSTANCE_DATE"] = pd.to_datetime(df["INSTANCE_DATE"], errors="coerce")
    df["TRANS_VALUE"] = pd.to_numeric(df["TRANS_VALUE"], errors="coerce")
    df["ACTUAL_AREA"] = pd.to_numeric(df["ACTUAL_AREA"], errors="coerce")

    valid = df["INSTANCE_DATE"].notna() & (df["TRANS_VALUE"] > 0)
    invalid_rows = int((~valid).sum())
    df = df[valid].reset_index(drop=True)

    audit = {
        "rows_loaded": rows_loaded,
        "exact_duplicates_removed": exact_duplicates,
        "duplicate_keys_with_different_data": duplicate_keys_left,
        "invalid_rows_removed": invalid_rows,
        "rows_final": len(df),
        "date_start": df["INSTANCE_DATE"].min(),
        "date_end": df["INSTANCE_DATE"].max(),
    }
    logger.info("Dataset audit: %s", audit)
    return df, audit



# Helpers

def _sales(df: pd.DataFrame) -> pd.DataFrame:
    """Keep sales transactions only."""
    return df[df["GROUP_EN"] == "Sales"]


def _coverage(df: pd.DataFrame) -> str:
    start, end = df["INSTANCE_DATE"].min(), df["INSTANCE_DATE"].max()
    return f"{start:%Y-%m-%d} to {end:%Y-%m-%d}"


def _result(metric, unit, filters, sample_size, df, value, warnings) -> dict:
    """Build a result dictionary in the shape the prompts expect."""
    return {
        "metric": metric,
        "unit": unit,
        "filters": filters,
        "sample_size": sample_size,
        "date_coverage": _coverage(df),
        "value": value,
        "warnings": "; ".join(warnings) if warnings else "none",
    }


def _resolve_area(df: pd.DataFrame, area: str) -> tuple[str | None, list[str]]:
    """Match an area name ignoring case. Return (match, close_suggestions)."""
    names = df["AREA_EN"].dropna().unique().tolist()
    lookup = {name.lower(): name for name in names}
    key = area.strip().lower()
    if key in lookup:
        return lookup[key], []
    return None, difflib.get_close_matches(area.strip(), names, n=3, cutoff=0.6)


def _area_not_found(metric, unit, area, df, suggestions) -> dict:
    warning = f"Area '{area}' not found in the dataset."
    if suggestions:
        warning += f" Similar names: {', '.join(suggestions)}."
    return _result(metric, unit, f"area={area}", 0, df, None, [warning])


def _small_sample_warning(count: int) -> list[str]:
    if count == 0:
        return ["No matching transactions."]
    if count < MIN_SAMPLE_SIZE:
        return [
            f"Only {count} matching transactions (fewer than {MIN_SAMPLE_SIZE}); "
            "the median is not reliable."
        ]
    return []

# Tools
def monthly_sales_count(df: pd.DataFrame) -> dict:
    """Count sales transactions per calendar month."""
    sales = _sales(df)
    counts = sales["INSTANCE_DATE"].dt.to_period("M").value_counts().sort_index()
    value = {str(period): int(n) for period, n in counts.items()}

    warnings = []
    last_date = sales["INSTANCE_DATE"].max()
    month_end = last_date.normalize() + pd.offsets.MonthEnd(0)
    if last_date.normalize() < month_end:
        warnings.append(
            f"{last_date:%Y-%m} is a partial month (data ends {last_date:%Y-%m-%d}); "
            "do not compare it with full months."
        )
    return _result("monthly_sales_count", "count", "group=Sales", len(sales), df, value, warnings)


def median_sale_value(
    df: pd.DataFrame, area: str | None = None, subtype: str | None = None
) -> dict:
    """Median sale value in AED, optionally for one area and/or subtype."""
    sales = _sales(df)
    filters = ["group=Sales"]
    warnings: list[str] = []

    if area:
        matched, suggestions = _resolve_area(df, area)
        if matched is None:
            return _area_not_found("median_sale_value", "AED", area, df, suggestions)
        sales = sales[sales["AREA_EN"] == matched]
        filters.append(f"area={matched}")

    if subtype:
        sales = sales[sales["PROP_SB_TYPE_EN"].str.lower() == subtype.strip().lower()]
        filters.append(f"property_subtype={subtype.strip()}")

    count = len(sales)
    warnings += _small_sample_warning(count)
    value = round(float(sales["TRANS_VALUE"].median()), 2) if count else None
    return _result("median_sale_value", "AED", "; ".join(filters), count, df, value, warnings)


def median_price_per_sqm(df: pd.DataFrame, area: str | None = None) -> dict:
    """Median price per square metre (AED/sq m) for Unit-type sales only.

    Land and Building rows are excluded because they are not comparable
    with individual units.
    """
    units = _sales(df)
    units = units[(units["PROP_TYPE_EN"] == "Unit") & (units["ACTUAL_AREA"] > 0)]
    filters = ["group=Sales", "property_type=Unit", "actual_area>0"]

    if area:
        matched, suggestions = _resolve_area(df, area)
        if matched is None:
            return _area_not_found("median_price_per_sqm", "AED per sq m", area, df, suggestions)
        units = units[units["AREA_EN"] == matched]
        filters.append(f"area={matched}")

    count = len(units)
    warnings = _small_sample_warning(count)
    value = None
    if count:
        value = round(float((units["TRANS_VALUE"] / units["ACTUAL_AREA"]).median()), 2)
    return _result(
        "median_price_per_sqm", "AED per sq m", "; ".join(filters), count, df, value, warnings
    )


def compare_price_per_sqm(df: pd.DataFrame, area_a: str, area_b: str) -> dict:
    """Compare median price per sq m between two areas."""
    first = median_price_per_sqm(df, area_a)
    second = median_price_per_sqm(df, area_b)

    warnings = [w for r in (first, second) for w in [r["warnings"]] if w != "none"]
    value = {area_a: first["value"], area_b: second["value"]}
    sizes = {area_a: first["sample_size"], area_b: second["sample_size"]}
    return _result(
        "compare_price_per_sqm",
        "AED per sq m",
        f"group=Sales; property_type=Unit; areas={area_a} vs {area_b}",
        sizes,
        df,
        value,
        warnings,
    )


def top_areas_by_count(df: pd.DataFrame, n: int = 5) -> dict:
    """Areas with the most sales transactions."""
    if n < 1:
        raise ValueError("n must be at least 1")
    sales = _sales(df)
    counts = sales["AREA_EN"].value_counts().head(n)
    value = {area: int(c) for area, c in counts.items()}
    return _result(f"top_{n}_areas_by_count", "count", "group=Sales", len(sales), df, value, [])


def offplan_share(df: pd.DataFrame) -> dict:
    """Share of sales that are off-plan versus ready."""
    sales = _sales(df)
    counts = sales["IS_OFFPLAN_EN"].value_counts()
    total = int(counts.sum())
    value = {
        status: {"count": int(c), "percent": round(100 * c / total, 1)}
        for status, c in counts.items()
    }
    return _result("offplan_share", "percent of sales", "group=Sales", total, df, value, [])