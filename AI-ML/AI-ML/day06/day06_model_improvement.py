
import pandas as pd
import numpy as np
from pathlib import Path

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    median_absolute_error
)

ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT / "DataSets"
REPORT_DIR = Path(__file__).parent / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

RANDOM_SEED = 42

# Load original CSV files
files = sorted(DATA_DIR.glob("*.csv"))
if not files:
    raise FileNotFoundError(f"No CSV files found in {DATA_DIR}")

df = pd.concat(
    [pd.read_csv(file, low_memory=False) for file in files],
    ignore_index=True
)

# Apply the same eligible-sales filters as previous days
procedure = (
    df["PROCEDURE_EN"].astype("string")
    .str.strip().str.lower()
    .str.replace(r"\s+", " ", regex=True)
)

df = df[
    (df["GROUP_EN"].astype("string").str.strip().str.lower() == "sales")
    & procedure.isin(["sale", "sell - pre registration"])
    & (df["TRANS_VALUE"] > 0)
    & (df["ACTUAL_AREA"] > 0)
].copy()

df["INSTANCE_DATE"] = pd.to_datetime(
    df["INSTANCE_DATE"], errors="coerce"
)
df = df.dropna(subset=["INSTANCE_DATE"])
df = df.sort_values("INSTANCE_DATE").reset_index(drop=True)

# Reproduce chronological 70/15/15 split
n = len(df)
train_end = int(n * 0.70)
validation_end = int(n * 0.85)

train_cutoff = df.loc[train_end - 1, "INSTANCE_DATE"]
validation_cutoff = df.loc[validation_end - 1, "INSTANCE_DATE"]

train = df[df["INSTANCE_DATE"] <= train_cutoff]
validation = df[
    (df["INSTANCE_DATE"] > train_cutoff)
    & (df["INSTANCE_DATE"] <= validation_cutoff)
]
test = df[df["INSTANCE_DATE"] > validation_cutoff]

numeric_features = ["ACTUAL_AREA"]

categorical_features = [
    "AREA_EN", "PROP_TYPE_EN", "PROP_SB_TYPE_EN",
    "ROOMS_EN", "PARKING", "IS_OFFPLAN_EN",
    "IS_FREE_HOLD_EN", "USAGE_EN"
]

features = numeric_features + categorical_features
target = "TRANS_VALUE"

# Preprocessing
numeric_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="median"))
])

categorical_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("encoder", OneHotEncoder(
        handle_unknown="ignore",
        min_frequency=20
    ))
])

preprocessor = ColumnTransformer([
    ("numeric", numeric_pipeline, numeric_features),
    ("categorical", categorical_pipeline, categorical_features)
])

# Median baseline
baseline = Pipeline([
    ("preprocessing", preprocessor),
    ("model", DummyRegressor(strategy="median"))
])

baseline.fit(train[features], train[target])

# Candidate Random Forest configurations
candidates = [
    {"max_depth": 12, "min_samples_leaf": 5},
    {"max_depth": 20, "min_samples_leaf": 5}
]

tuning_results = []
best_model = None
best_config = None
best_validation_mae = float("inf")

for config in candidates:
    model = Pipeline([
        ("preprocessing", preprocessor),
        ("model", RandomForestRegressor(
            n_estimators=80,
            max_depth=config["max_depth"],
            min_samples_leaf=config["min_samples_leaf"],
            random_state=RANDOM_SEED,
            n_jobs=-1
        ))
    ])

    model.fit(train[features], train[target])

    validation_predictions = model.predict(validation[features])

    validation_mae = mean_absolute_error(
        validation[target], validation_predictions
    )

    tuning_results.append({
        "max_depth": config["max_depth"],
        "min_samples_leaf": config["min_samples_leaf"],
        "n_estimators": 80,
        "random_seed": RANDOM_SEED,
        "validation_MAE": validation_mae
    })

    print(
        f"Tested configuration {config}: "
        f"Validation MAE = {validation_mae:.2f}"
    )

    if validation_mae < best_validation_mae:
        best_validation_mae = validation_mae
        best_model = model
        best_config = config

# Save validation tuning results
pd.DataFrame(tuning_results).to_csv(
    REPORT_DIR / "day06_tuning_results.csv",
    index=False
)

# Evaluate baseline and selected model
evaluation_results = []

for model_name, model in [
    ("Median Baseline", baseline),
    ("Random Forest", best_model)
]:
    for split_name, split_data in [
        ("validation", validation),
        ("test", test)
    ]:
        actual = split_data[target]
        predicted = model.predict(split_data[features])

        evaluation_results.append({
            "model": model_name,
            "split": split_name,
            "rows": len(split_data),
            "MAE": mean_absolute_error(actual, predicted),
            "RMSE": np.sqrt(mean_squared_error(actual, predicted)),
            "Median_Absolute_Error": median_absolute_error(
                actual, predicted
            )
        })

metrics = pd.DataFrame(evaluation_results)

metrics.to_csv(
    REPORT_DIR / "day06_model_comparison.csv",
    index=False
)

print("\nDAY 6 MODEL IMPROVEMENT COMPLETED")
print("\nSelected Random Forest configuration:", best_config)
print("\nModel comparison:")
print(metrics.to_string(index=False))
print("\nRandom seed:", RANDOM_SEED)
print("Tuning performed using validation data.")
print("Test set kept separate for final evaluation.")
print("Reports saved in:", REPORT_DIR)
