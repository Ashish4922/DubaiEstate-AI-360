
from __future__ import annotations

import argparse
import logging
from datetime import date
from pathlib import Path

import pandas as pd

from Genai import retrieval
from Genai.prompts import DISCLAIMER
from Genai.retrieval import MIN_SAMPLE_SIZE, load_transactions

DEFAULT_OUTPUT = Path("genai/reports/market_summary_draft.md")
TOP_AREAS = 5
EXAMPLE_ROWS = 3


class _References:
    """Collects citations and hands out reference numbers (A1, A2, ... / R1, R2, ...)."""

    def __init__(self) -> None:
        self._items: list[tuple[str, str, str, object, str]] = []

    def add(self, prefix: str, source: str, filters: str, sample_size, coverage: str) -> str:
        number = sum(1 for item in self._items if item[0].startswith(prefix)) + 1
        ref = f"{prefix}{number}"
        self._items.append((ref, source, filters, sample_size, coverage))
        return ref

    def from_result(self, result: dict, source: str) -> str:
        return self.add("A", source, result["filters"], result["sample_size"], result["date_coverage"])

    def table(self) -> list[str]:
        lines = [
            "| Ref | Source | Filters | Sample size | Date coverage |",
            "|---|---|---|---|---|",
        ]
        for ref, source, filters, size, coverage in self._items:
            size_text = f"{size:,}" if isinstance(size, int) else str(size)
            lines.append(f"| {ref} | `{source}` | {filters} | {size_text} | {coverage} |")
        return lines


def _money(value: float | None) -> str:
    return f"AED {value:,.0f}" if value is not None else "no figure"


def build_report(df: pd.DataFrame, audit: dict, today: date | None = None) -> str:
    """Return the market-summary draft as Markdown text."""
    today = today or date.today()
    refs = _References()

    start = pd.Timestamp(audit["date_start"])
    end = pd.Timestamp(audit["date_end"])
    coverage = f"{start:%Y-%m-%d} to {end:%Y-%m-%d}"

    # ---- Run every tool once and register its citation -------------------
    audit_ref = refs.add("A", "retrieval.load_transactions()", "all rows in both CSV parts",
                         audit["rows_loaded"], coverage)

    monthly = retrieval.monthly_sales_count(df)
    monthly_ref = refs.from_result(monthly, "retrieval.monthly_sales_count(df)")

    top = retrieval.top_areas_by_count(df, TOP_AREAS)
    top_ref = refs.from_result(top, f"retrieval.top_areas_by_count(df, {TOP_AREAS})")

    offplan = retrieval.offplan_share(df)
    offplan_ref = refs.from_result(offplan, "retrieval.offplan_share(df)")

    overall_sqm = retrieval.median_price_per_sqm(df)
    overall_sqm_ref = refs.from_result(overall_sqm, "retrieval.median_price_per_sqm(df)")

    area_sqm = []
    for area in top["value"]:
        result = retrieval.median_price_per_sqm(df, area)
        ref = refs.from_result(result, f"retrieval.median_price_per_sqm(df, '{area}')")
        area_sqm.append((area, result, ref))

    total_sales = top["sample_size"]
    partial = "partial month" in monthly["warnings"]
    months = list(monthly["value"].items())
    full_months = months[:-1] if partial else months

    # ---- Write the report -------------------------------------------------
    out = [
        "# Dubai Property Transactions: Market Summary (DRAFT)",
        "",
        f"*Generated on {today:%Y-%m-%d} from the project dataset. Draft for review. "
        f"{DISCLAIMER}*",
        "",
        "## 1. Dataset overview",
        f"- Rows loaded from both CSV parts: {audit['rows_loaded']:,} [{audit_ref}]",
        f"- Exact duplicate rows removed: {audit['exact_duplicates_removed']:,} [{audit_ref}]",
        f"- Transaction numbers that still appear more than once with different data "
        f"(kept, not removed): {audit['duplicate_keys_with_different_data']:,} [{audit_ref}]",
        f"- Rows removed as invalid (unparseable date or non-positive value): "
        f"{audit['invalid_rows_removed']:,} [{audit_ref}]",
        f"- Rows used in this report: {audit['rows_final']:,} [{audit_ref}]",
        f"- Date coverage: {coverage} [{audit_ref}]",
        "",
        "## 2. Sales activity by month",
        f"Sales transactions per calendar month [{monthly_ref}]:",
        "",
        "| Month | Sales transactions |",
        "|---|---|",
    ]
    for index, (month, count) in enumerate(months):
        label = f"{month} (partial, data to {end:%Y-%m-%d})" if partial and index == len(months) - 1 else month
        out.append(f"| {label} | {count:,} |")

    if full_months:
        busiest = max(full_months, key=lambda item: item[1])
        quietest = min(full_months, key=lambda item: item[1])
        out += [
            "",
            f"Among complete months, {busiest[0]} had the most sales ({busiest[1]:,}) and "
            f"{quietest[0]} had the fewest ({quietest[1]:,}) [{monthly_ref}].",
        ]
    if partial:
        out.append(f"The last month is incomplete, so it should not be compared with full months [{monthly_ref}].")

    out += [
        "",
        f"## 3. Most active areas (top {TOP_AREAS} by number of sales)",
        f"Total sales used: {total_sales:,} [{top_ref}].",
        "",
        "| Rank | Area | Sales transactions | Share of all sales |",
        "|---|---|---|---|",
    ]
    for rank, (area, count) in enumerate(top["value"].items(), start=1):
        out.append(f"| {rank} | {area} | {count:,} | {100 * count / total_sales:.1f}% |")
    out.append(f"\nSource for counts and shares: [{top_ref}].")

    out += ["", "## 4. Off-plan versus ready", f"Share of sales by status [{offplan_ref}]:", "",
            "| Status | Sales transactions | Share |", "|---|---|---|"]
    for status, values in offplan["value"].items():
        out.append(f"| {status} | {values['count']:,} | {values['percent']}% |")

    out += [
        "",
        f"## 5. Median price per square metre (units only)",
        f"Across all unit-type sales, the median is {_money(overall_sqm['value'])} per sq m "
        f"(sample {overall_sqm['sample_size']:,}) [{overall_sqm_ref}]. "
        "Land and building sales are excluded because they are not comparable with individual units.",
        "",
        "| Area | Median AED per sq m | Unit sales in sample | Note |",
        "|---|---|---|---|",
    ]
    for area, result, ref in area_sqm:
        size = result["sample_size"]
        if result["value"] is None:
            note = "no unit sales in this area"
        elif size < MIN_SAMPLE_SIZE:
            note = f"small sample (under {MIN_SAMPLE_SIZE}), not reliable"
        else:
            note = ""
        out.append(f"| {area} [{ref}] | {_money(result['value']).replace('AED ', '')} | {size:,} | {note} |")

    sales = df[df["GROUP_EN"] == "Sales"]
    out += [
        "",
        "## 6. Example transactions",
        f"The largest recorded sale in each of the top {EXAMPLE_ROWS} areas, so the figures "
        "above can be traced to real rows:",
        "",
        "| Ref | Area | Transaction number | Date | Value (AED) | Area (sq m) |",
        "|---|---|---|---|---|---|",
    ]
    for area in list(top["value"])[:EXAMPLE_ROWS]:
        row = sales[sales["AREA_EN"] == area].nlargest(1, "TRANS_VALUE").iloc[0]
        ref = refs.add(
            "R",
            "largest sale in area",
            f"TRANSACTION_NUMBER={row['TRANSACTION_NUMBER']}; area={area}",
            "1 row",
            f"{row['INSTANCE_DATE']:%Y-%m-%d}",
        )
        out.append(
            f"| [{ref}] | {area} | {row['TRANSACTION_NUMBER']} | {row['INSTANCE_DATE']:%Y-%m-%d} "
            f"| {row['TRANS_VALUE']:,.0f} | {row['ACTUAL_AREA']:,.2f} |"
        )

    out += [
        "",
        "## 7. Limitations",
        "- The report describes past transactions only. It makes no statement about future prices.",
        "- The dataset has no rent, occupancy, tenancy or maintenance fields, so none are discussed.",
        "- Medians are used because a few very large sales would distort averages.",
        f"- Medians based on fewer than {MIN_SAMPLE_SIZE} rows are marked unreliable "
        "(a project convention, not a statistical rule).",
        "- Some transaction numbers appear more than once with different data. Both rows were kept "
        "because the correct one cannot be determined from the file.",
        "- Subtype labels are inconsistent in the source and some are blank, so this report "
        "groups by area and status rather than by subtype.",
        "- Area names are used exactly as written in the source data.",
        "",
        "## 8. Sources",
        "",
        *refs.table(),
        "",
        f"*{DISCLAIMER}*",
        "",
    ]
    return "\n".join(out)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the market-summary draft")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    logging.basicConfig(level=logging.WARNING)
    df, audit = load_transactions()
    report = build_report(df, audit)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report, encoding="utf-8")
    print(f"Report written to {args.output}")


if __name__ == "__main__":
    main()