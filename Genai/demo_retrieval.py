import logging

from Genai.prompts import format_verified_result
from Genai.retrieval import (
    compare_price_per_sqm,
    load_transactions,
    median_price_per_sqm,
    median_sale_value,
    monthly_sales_count,
    offplan_share,
    top_areas_by_count,
)


def show(title: str, result: dict) -> None:
    print(f"\n=== {title} ===")
    print(format_verified_result(result))


def main() -> None:
    logging.basicConfig(level=logging.WARNING)
    df, audit = load_transactions()

    print("=== DATASET AUDIT ===")
    for key, value in audit.items():
        print(f"{key}: {value}")

    show("Monthly sales", monthly_sales_count(df))
    show("Top 5 areas", top_areas_by_count(df, 5))
    show("Off-plan share", offplan_share(df))
    show("Median value, all flats", median_sale_value(df, subtype="Flat"))
    show("Median price per sq m, all units", median_price_per_sqm(df))
    show("Compare two areas", compare_price_per_sqm(df, "Business Bay", "Marina"))
    show("Unknown area", median_sale_value(df, area="Atlantis"))


if __name__ == "__main__":
    main()