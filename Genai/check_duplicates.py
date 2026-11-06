from pathlib import Path

import pandas as pd

DATA_DIR = Path("DataSets")
PARTS = [
    DATA_DIR / "dubai_transactions_2026_part_1.csv",
    DATA_DIR / "dubai_transactions_2026_part_2.csv",
]


def main() -> None:
    frames = []
    for i, path in enumerate(PARTS, start=1):
        part = pd.read_csv(path, low_memory=False)
        part["SOURCE_PART"] = i
        frames.append(part)
    df = pd.concat(frames, ignore_index=True)

    key = "TRANSACTION_NUMBER"
    dup_rows = df[df[key].duplicated(keep=False)].sort_values(key)
    print("Rows involved in duplicate keys:", len(dup_rows))
    print("Distinct duplicated keys:", dup_rows[key].nunique())

    # Do the duplicates come from within one file or across both files?
    print("\nSource parts of duplicate rows:")
    print(dup_rows["SOURCE_PART"].value_counts())

    # Are they exact copies once we ignore our helper column?
    data_cols = [c for c in df.columns if c != "SOURCE_PART"]
    exact = df.duplicated(subset=data_cols, keep=False) & df[key].duplicated(keep=False)
    print("Duplicate-key rows that are exact full-row copies:", exact.sum())

    print("\nSample of duplicate rows:")
    print(dup_rows[[key, "INSTANCE_DATE", "AREA_EN", "TRANS_VALUE", "ACTUAL_AREA", "SOURCE_PART"]].head(10))


if __name__ == "__main__":
    main()