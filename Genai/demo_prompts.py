from Genai.prompts import (
    SYSTEM_PROMPT,
    build_answer_prompt,
    build_refusal_prompt,
    format_verified_result,
)

EXAMPLE_RESULT = {
    "metric": "median_sale_value",
    "unit": "AED",
    "filters": "property_subtype=Flat; area=EXAMPLE AREA",
    "sample_size": 100,  # placeholder
    "date_coverage": "2026-01-01 to 2026-10-29",
    "value": 1000000,  # placeholder
    "warnings": "none",
}


def main() -> None:
    print("=== SYSTEM PROMPT ===")
    print(SYSTEM_PROMPT)

    print("=== ANSWER PROMPT (placeholder figures) ===")
    block = format_verified_result(EXAMPLE_RESULT)
    print(build_answer_prompt("What is the median price of flats in EXAMPLE AREA?", block))

    print("=== REFUSAL PROMPT ===")
    print(
        build_refusal_prompt(
            "Will prices in Marina go up next year?",
            "The dataset holds past transactions only and cannot support predictions.",
        )
    )

    print("=== INCOMPLETE RESULT TEST ===")
    try:
        format_verified_result({"metric": "count"})
    except ValueError as error:
        print("Correctly rejected:", error)


if __name__ == "__main__":
    main()