
from pathlib import Path
import pandas as pd


def find_dataset_directory():
    current = Path(__file__).resolve()

    for parent in current.parents:
        folder = parent / "DataSets"
        if folder.is_dir():
            return folder

    raise FileNotFoundError("DataSets directory not found.")


def load_transactions():
    data_dir = find_dataset_directory()

    file1 = data_dir / "dubai_transactions_2026_part_1.csv"
    file2 = data_dir / "dubai_transactions_2026_part_2.csv"

    df1 = pd.read_csv(file1, low_memory=False)
    df2 = pd.read_csv(file2, low_memory=False)

    if set(df1.columns) != set(df2.columns):
        raise ValueError("Dataset schemas do not match.")

    return pd.concat(
        [df1, df2[df1.columns]],
        ignore_index=True
    )


def analyze_procedures(df):
    print("\n========== DAY 8: PROCEDURE ANALYSIS ==========")

    procedure_summary = (
        df.groupby("PROCEDURE_EN", dropna=False)
        .agg(
            Transaction_Count=("TRANS_VALUE", "count"),
            Average_Value=("TRANS_VALUE", "mean"),
            Median_Value=("TRANS_VALUE", "median"),
            Minimum_Value=("TRANS_VALUE", "min"),
            Maximum_Value=("TRANS_VALUE", "max")
        )
        .sort_values("Transaction_Count", ascending=False)
    )

    print("\nProcedure-wise transaction summary:")
    print(procedure_summary.to_string())

    # Identify potential sale-related categories.
    sale_mask = (
        df["PROCEDURE_EN"]
        .astype("string")
        .str.contains(r"\bsell\b|\bsale\b", case=False, na=False)
    )

    candidate_sales = df.loc[sale_mask].copy()
    other_transactions = df.loc[~sale_mask].copy()

    print("\n========== CANDIDATE SALE CATEGORIES ==========")

    print(
        candidate_sales["PROCEDURE_EN"]
        .value_counts()
        .to_string()
    )

    print("\nCandidate sale records:", len(candidate_sales))
    print("Other procedure records:", len(other_transactions))

    print("\nCandidate sale dataset shape:", candidate_sales.shape)

    print("\nDay 8 procedure analysis completed.")


def main():
    df = load_transactions()

    print("Original dataset shape:", df.shape)

    analyze_procedures(df)


if __name__ == "__main__":
    main()
