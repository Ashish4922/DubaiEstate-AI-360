
"""Local deterministic assistant for Dubai real-estate transaction metrics."""

import csv
from pathlib import Path

try:
    from .data_retrieval import get_transaction_metrics
except ImportError:
    from data_retrieval import get_transaction_metrics


DATA_DIR = Path(__file__).resolve().parent.parent / "DataSets"

CSV_PATHS = [
    DATA_DIR / "dubai_transactions_2026_part_1.csv",
    DATA_DIR / "dubai_transactions_2026_part_2.csv",
]


def _load_areas() -> list[str]:
    """Read known area names from the source CSVs."""
    areas: set[str] = set()

    for path in CSV_PATHS:
        with path.open(encoding="utf-8-sig", newline="") as source:
            reader = csv.DictReader(source)

            if "AREA_EN" not in (reader.fieldnames or []):
                raise ValueError(f"{path}: missing required column AREA_EN")

            for row in reader:
                area = (row.get("AREA_EN") or "").strip()
                if area:
                    areas.add(area)

    return sorted(areas, key=str.casefold)


def _format_metrics(
    metrics: dict,
    area: str | None = None,
) -> str:
    """Format retrieved metrics without inventing values."""
    scope = f" for {area}" if area else " across the dataset"

    count = metrics["transaction_count"]
    total = metrics["total_value"]
    average = metrics["average_value"]

    if count == 0:
        return f"No matching transactions were found{scope}."

    return (
        f"Transaction summary{scope}:\n"
        f"- Transaction count: {count:,}\n"
        f"- Total transaction value: AED {total:,.2f}\n"
        f"- Average transaction value: AED {average:,.2f}\n"
        "Source: local Dubai transaction CSV dataset."
    )


def answer_question(question: str) -> str:
    """Answer supported transaction-metric questions deterministically."""
    if not question or not question.strip():
        return "Please enter a question about transaction metrics."

    normalized = question.casefold()

    supported_terms = (
        "transaction",
        "average",
        "avg",
        "total value",
        "total transaction",
        "how many",
        "count",
        "metrics",
    )

    if not any(term in normalized for term in supported_terms):
        return (
            "I can't answer that question with the currently supported "
            "transaction metrics. Try asking about transaction count, "
            "total transaction value, or average transaction value."
        )

    # Load area names only after confirming the question is supported.
    areas = _load_areas()
    area_match = None

    for area in areas:
        if area.casefold() in normalized:
            area_match = area
            break

    # Don't silently return dataset-wide metrics for an unknown area.
    if area_match is None and any(
        phrase in normalized
        for phrase in (" in ", " for ", " area ")
    ):
        return (
            "I couldn't identify that area in the dataset. "
            "Please use an area name from the available dataset."
        )

    metrics = get_transaction_metrics(
        CSV_PATHS,
        area=area_match,
    )

    return _format_metrics(metrics, area_match)


if __name__ == "__main__":
    user_question = input("Ask about Dubai transaction metrics: ")
    print(answer_question(user_question))
