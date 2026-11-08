"""Deterministic retrieval of transaction metrics from validated CSV files."""

import csv
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Iterable

REQUIRED_COLUMNS = {"INSTANCE_DATE", "AREA_EN", "TRANS_VALUE"}
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_transaction_metrics(
    csv_paths: Iterable[str | Path], *, area: str | None = None,
    start_date: date | None = None, end_date: date | None = None,
) -> dict[str, int | Decimal | None]:
    """Return count, total, and average for matching rows.

    Area matching is exact after trimming whitespace. Date bounds are inclusive.
    Source files are read only, and rows are not deduplicated because repeated
    transaction numbers can have conflicting data.
    """
    if start_date and end_date and start_date > end_date:
        raise ValueError("start_date must be on or before end_date")
    if area is not None and not area.strip():
        raise ValueError("area must not be blank")

    count, total = 0, Decimal("0")
    for csv_path in csv_paths:
        path = Path(csv_path)
        with path.open(encoding="utf-8-sig", newline="") as source:
            reader = csv.DictReader(source)
            missing = REQUIRED_COLUMNS - set(reader.fieldnames or ())
            if missing:
                raise ValueError(f"{path}: missing required columns: {', '.join(sorted(missing))}")
            for row_number, row in enumerate(reader, start=2):
                try:
                    instance_date = datetime.strptime(row["INSTANCE_DATE"].strip(), DATE_FORMAT).date()
                    value = Decimal(row["TRANS_VALUE"].strip())
                except (AttributeError, InvalidOperation, ValueError) as exc:
                    raise ValueError(f"{path}: invalid date or transaction value on row {row_number}") from exc
                if not value.is_finite():
                    raise ValueError(f"{path}: invalid transaction value on row {row_number}")

                row_area = (row.get("AREA_EN") or "").strip()
                if area is not None and row_area != area.strip():
                    continue
                if start_date is not None and instance_date < start_date:
                    continue
                if end_date is not None and instance_date > end_date:
                    continue
                count += 1
                total += value

    return {
        "transaction_count": count,
        "total_value": total,
        "average_value": total / count if count else None,
    }
