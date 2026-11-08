from pathlib import Path

import pandas as pd

DATA_DIR = Path("DataSets")
PARTS = [
    DATA_DIR / "dubai_transactions_2026_part_1.csv",
    DATA_DIR / "dubai_transactions_2026_part_2.csv",
]


def main() -> None:
    frames = [pd.read_csv(p, low_memory=False) for p in PARTS]
    df = pd.concat(frames, ignore_index=True)
    df["INSTANCE_DATE"] = pd.to_datetime(df["INSTANCE_DATE"], errors="coerce")

    print("Total rows:", len(df))
    print("Unparseable dates:", df["INSTANCE_DATE"].isna().sum())
    print("Date range:", df["INSTANCE_DATE"].min(), "to", df["INSTANCE_DATE"].max())
    print("Duplicate TRANSACTION_NUMBER:", df["TRANSACTION_NUMBER"].duplicated().sum())

    for col in ["GROUP_EN", "IS_OFFPLAN_EN", "USAGE_EN", "PROP_TYPE_EN", "PROP_SB_TYPE_EN"]:
        print(f"\n--- {col} ---")
        print(df[col].value_counts(dropna=False).head(15))

    print("\n--- Rows per month ---")
    print(df["INSTANCE_DATE"].dt.to_period("M").value_counts().sort_index())

    print("\nTRANS_VALUE <= 0:", (df["TRANS_VALUE"] <= 0).sum())
    print("ACTUAL_AREA <= 0 or missing:", (df["ACTUAL_AREA"].fillna(0) <= 0).sum())
    print("Unique areas:", df["AREA_EN"].nunique())


if __name__ == "__main__":
    main()