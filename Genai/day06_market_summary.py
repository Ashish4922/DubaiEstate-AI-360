"""Generate a reproducible Dubai transaction market summary."""

import csv
from collections import defaultdict
from decimal import Decimal
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "DataSets"
OUTPUT = Path(__file__).resolve().parent

FILES = [
    DATA_DIR / "dubai_transactions_2026_part_1.csv",
    DATA_DIR / "dubai_transactions_2026_part_2.csv",
]

REQUIRED = {
    "TRANSACTION_NUMBER", "INSTANCE_DATE", "GROUP_EN",
    "AREA_EN", "TRANS_VALUE", "ACTUAL_AREA",
}


def load_records():
    records = []

    for path in FILES:
        if not path.exists():
            raise FileNotFoundError(f"Missing source file: {path}")

        with path.open(encoding="utf-8-sig", newline="") as source:
            reader = csv.DictReader(source)
            missing = REQUIRED - set(reader.fieldnames or [])

            if missing:
                raise ValueError(f"{path.name}: missing columns {sorted(missing)}")

            for row_number, row in enumerate(reader, start=2):
                try:
                    value = Decimal(row["TRANS_VALUE"].strip())
                    area_raw = row["ACTUAL_AREA"].strip()
                    area_sqm = Decimal(area_raw) if area_raw else None
                except Exception as exc:
                    raise ValueError(
                        f"{path.name}, row {row_number}: invalid numeric value"
                    ) from exc

                records.append({
                    "file": path.name,
                    "row": row_number,
                    "transaction_number": row["TRANSACTION_NUMBER"],
                    "date": row["INSTANCE_DATE"],
                    "group": row["GROUP_EN"],
                    "area": row["AREA_EN"].strip(),
                    "value": value,
                    "area_sqm": area_sqm,
                })

    return records


def main():
    records = load_records()

    if not records:
        raise ValueError("No records found.")

    sales = [r for r in records if r["group"] == "Sales"]
    valid_values = [r for r in sales if r["value"] > 0]

    valid_price_sqm = [
        r for r in valid_values
        if r["area_sqm"] is not None and r["area_sqm"] > 0
    ]

    values = [r["value"] for r in valid_values]
    prices_sqm = [
        r["value"] / r["area_sqm"] for r in valid_price_sqm
    ]

    area_groups = defaultdict(list)
    for r in valid_price_sqm:
        area_groups[r["area"]].append(r)

    top_areas = sorted(
        area_groups.items(),
        key=lambda item: (-len(item[1]), item[0].casefold())
    )[:10]

    dates = sorted(r["date"] for r in sales)

    report = [
        "# Dubai Real Estate Transaction Market Summary",
        "",
        "## Reporting scope",
        "",
        f"- Source files: {len(FILES)} CSV files",
        f"- Total source records: {len(records):,}",
        f"- Sales records: {len(sales):,}",
        f"- Reporting period: {dates[0]} to {dates[-1]}",
        "- Dataset: Dubai transaction CSV files for 2026",
        "",
        "## Dataset-level findings",
        "",
        f"- Valid positive-value sales: {len(valid_values):,}",
        f"- Total transaction value: AED {sum(values):,.2f}",
        f"- Average transaction value: AED {sum(values) / len(values):,.2f}",
        f"- Median transaction value: AED {median(values):,.2f}",
        f"- Minimum transaction value: AED {min(values):,.2f}",
        f"- Maximum transaction value: AED {max(values):,.2f}",
        f"- Valid price-per-sqm records: {len(valid_price_sqm):,}",
        f"- Median price per sqm: AED {median(prices_sqm):,.2f}",
        f"- Average price per sqm: AED {sum(prices_sqm) / len(prices_sqm):,.2f}",
        "",
        "## Area comparison",
        "",
        "Top 10 areas by transaction count among records with positive "
        "transaction values and positive ACTUAL_AREA:",
        "",
        "| Area | Transaction count | Median AED/sqm |",
        "|---|---:|---:|",
    ]

    for area, rows in top_areas:
        area_prices = [r["value"] / r["area_sqm"] for r in rows]
        report.append(
            f"| {area} | {len(rows):,} | {median(area_prices):,.2f} |"
        )

    report.extend([
        "",
        "## Methodology",
        "",
        "- Read both original CSV files without modifying them.",
        "- Include rows with GROUP_EN equal to Sales.",
        "- Transaction-value statistics use positive TRANS_VALUE values.",
        "- Price-per-sqm statistics require positive TRANS_VALUE and "
        "positive ACTUAL_AREA.",
        "- Price per sqm is calculated as TRANS_VALUE / ACTUAL_AREA.",
        "- Median is used to reduce sensitivity to extreme values.",
        "- Area rankings use transaction count, not price.",
        "- Original CSV row numbers include the header as row 1.",
        "",
        "## Source references",
        "",
        "Aggregate figures are reproducible from the source CSVs using "
        "the accompanying Python script.",
        "",
    ])

    evidence_path = OUTPUT / "day06_source_evidence.csv"

    with evidence_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "source_file", "csv_row", "transaction_number",
            "instance_date", "area", "transaction_value",
            "actual_area_sqm", "price_per_sqm"
        ])

        for r in valid_price_sqm:
            writer.writerow([
                r["file"], r["row"], r["transaction_number"],
                r["date"], r["area"], str(r["value"]),
                str(r["area_sqm"]),
                str(r["value"] / r["area_sqm"]),
            ])

    report.extend([
        f"- Record-level evidence: `{evidence_path.name}`",
        "- Evidence file includes source CSV filename, original CSV row, "
        "transaction number, date, area, value and price per sqm.",
        "",
        "## Limitations",
        "",
        "- Dataset coverage ends at the latest date shown above.",
        "- Dataset figures may not represent every Dubai transaction.",
        "- Transaction values and price-per-sqm distributions contain "
        "extreme observations.",
        "- Price per sqm uses ACTUAL_AREA; it may differ from other "
        "area definitions.",
        "- This is descriptive historical analysis, not investment advice.",
        "- No future returns or price forecasts are estimated.",
        "",
    ])

    report_path = OUTPUT / "day06_market_summary.md"
    report_path.write_text("\n".join(report), encoding="utf-8")

    print(f"Records: {len(records):,}")
    print(f"Sales: {len(sales):,}")
    print(f"Valid values: {len(valid_values):,}")
    print(f"Valid price/sqm: {len(valid_price_sqm):,}")
    print(f"Report created: {report_path}")
    print(f"Evidence created: {evidence_path}")


if __name__ == "__main__":
    main()
