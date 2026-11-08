from pathlib import Path

import pandas as pd

DATA_DIR = Path("DataSets")
PARTS = [
    DATA_DIR / "dubai_transactions_2026_part_1.csv",
    DATA_DIR / "dubai_transactions_2026_part_2.csv",
]


def main() -> None:
    for path in PARTS:
        df = pd.read_csv(path, low_memory=False)
        print(f"\n=== {path.name} ===")
        print("Shape:", df.shape)
        print("Columns:", list(df.columns))
        print(df.head(3).T)


if __name__ == "__main__":
    main()