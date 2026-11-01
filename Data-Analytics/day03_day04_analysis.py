
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

START_DATE = "2026-01-01"
END_DATE = "2026-10-29"
# --------------------------------------------------
# PROJECT PATHS AND SETTINGS
# --------------------------------------------------
# Premium Purple-Blue Chart Theme
BG_COLOR = "#0B1020"
PANEL_COLOR = "#151D35"
PURPLE = "#9B5DE5"
BLUE = "#4CC9F0"
TEXT_COLOR = "#F4F6FF"
MUTED_COLOR = "#AAB4D0"
GRID_COLOR = "#303B5B"
MIN_AREA_TRANSACTIONS = 30

START_DATE = "2026-01-01"
END_DATE = "2026-10-29"

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "DataSets"
OUTPUT_DIR = ROOT / "Data-Analytics" / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FILES = [
    DATA_DIR / "dubai_transactions_2026_part_1.csv",
    DATA_DIR / "dubai_transactions_2026_part_2.csv",
]

REQUIRED_COLUMNS = [
    "INSTANCE_DATE",
    "TRANSACTION_NUMBER",
    "TRANS_VALUE",
    "AREA_EN",
    "ACTUAL_AREA",
]

# --------------------------------------------------
# LOAD AND VALIDATE DATA
# --------------------------------------------------

print("\n========== LOADING DATA ==========")

for file in FILES:
    if not file.exists():
        raise FileNotFoundError(f"Dataset not found: {file}")

dataframes = [pd.read_csv(file) for file in FILES]

if list(dataframes[0].columns) != list(dataframes[1].columns):
    raise ValueError("Dataset headers do not match.")

df = pd.concat(dataframes, ignore_index=True)

missing_columns = [
    col for col in REQUIRED_COLUMNS if col not in df.columns
]

if missing_columns:
    raise ValueError(f"Missing columns: {missing_columns}")

df["INSTANCE_DATE"] = pd.to_datetime(
    df["INSTANCE_DATE"], errors="coerce"
)

df["TRANS_VALUE"] = pd.to_numeric(
    df["TRANS_VALUE"], errors="coerce"
)

df["ACTUAL_AREA"] = pd.to_numeric(
    df["ACTUAL_AREA"], errors="coerce"
)

print(f"Total records: {len(df):,}")
print(f"Valid dates: {df['INSTANCE_DATE'].notna().sum():,}")
print(
    f"Date range: {df['INSTANCE_DATE'].min()} to "
    f"{df['INSTANCE_DATE'].max()}"
)

# Do not remove repeated transaction IDs without confirmation.
# Each source record is retained for this analysis.

# --------------------------------------------------
# DAY 3: TIME-BASED ANALYSIS
# --------------------------------------------------

print("\n========== DAY 3: TIME ANALYSIS ==========")

valid_time = df.dropna(
    subset=["INSTANCE_DATE", "TRANS_VALUE"]
).copy()

# Apply explicit inclusive date filter
valid_time = valid_time[
    (valid_time["INSTANCE_DATE"] >= pd.Timestamp(START_DATE))
    & (
        valid_time["INSTANCE_DATE"]
        < pd.Timestamp(END_DATE) + pd.Timedelta(days=1)
    )
].copy()

if valid_time.empty:
    raise ValueError("No records found within the selected date range.")

valid_time["MONTH"] = (
    valid_time["INSTANCE_DATE"].dt.to_period("M")
)

monthly = (
    valid_time.groupby("MONTH")
    .agg(
        transaction_count=("TRANSACTION_NUMBER", "size"),
        total_transaction_value=("TRANS_VALUE", "sum"),
        median_transaction_value=("TRANS_VALUE", "median"),
    )
    .reset_index()
)

monthly["MONTH"] = monthly["MONTH"].astype(str)

# Save original numeric summary CSV
monthly.to_csv(
    OUTPUT_DIR / "day03_monthly_summary.csv",
    index=False
)

## Premium Monthly Transaction Count Chart

fig, ax = plt.subplots(figsize=(13, 7))
fig.patch.set_facecolor(BG_COLOR)
ax.set_facecolor(PANEL_COLOR)

bars = ax.bar(
    monthly["MONTH"],
    monthly["transaction_count"],
    color=PURPLE,
    width=0.65,
    edgecolor=BLUE,
    linewidth=1.2
)

ax.set_title(
    "Monthly Real Estate Transaction Count",
    fontsize=18,
    fontweight="bold",
    color=TEXT_COLOR,
    pad=22
)

ax.set_xlabel("Month", fontsize=12, color=TEXT_COLOR, labelpad=12)
ax.set_ylabel("Transaction Records", fontsize=12, color=TEXT_COLOR, labelpad=12)

ax.tick_params(axis="x", colors=MUTED_COLOR, rotation=35)
ax.tick_params(axis="y", colors=MUTED_COLOR)

ax.grid(axis="y", color=GRID_COLOR, linestyle="--", alpha=0.6)
ax.set_axisbelow(True)

for bar in bars:
    height = bar.get_height()
    ax.annotate(
        f"{height:,.0f}",
        (bar.get_x() + bar.get_width() / 2, height),
        xytext=(0, 7),
        textcoords="offset points",
        ha="center",
        fontsize=9,
        fontweight="bold",
        color=TEXT_COLOR
    )

for spine in ax.spines.values():
    spine.set_color(GRID_COLOR)

ax.margins(y=0.15)
plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "day03_monthly_transaction_count.png",
    dpi=300,
    facecolor=fig.get_facecolor(),
    bbox_inches="tight"
)
plt.close()

#
# Premium Monthly Transaction Value Chart

fig, ax = plt.subplots(figsize=(13, 7))
fig.patch.set_facecolor(BG_COLOR)
ax.set_facecolor(PANEL_COLOR)

x = range(len(monthly))
values = monthly["total_transaction_value"]

ax.plot(
    x,
    values,
    color=PURPLE,
    linewidth=3,
    marker="o",
    markersize=9,
    markerfacecolor=BLUE,
    markeredgecolor=TEXT_COLOR,
    markeredgewidth=1.5,
    label="Total Transaction Value"
)

ax.fill_between(
    x,
    values,
    color=PURPLE,
    alpha=0.18
)

ax.set_title(
    "Monthly Total Transaction Value",
    fontsize=18,
    fontweight="bold",
    color=TEXT_COLOR,
    pad=22
)

ax.set_xlabel("Month", fontsize=12, color=TEXT_COLOR, labelpad=12)
ax.set_ylabel(
    "Total Transaction Value (Source Units)",
    fontsize=12,
    color=TEXT_COLOR,
    labelpad=12
)

ax.set_xticks(list(x))
ax.set_xticklabels(monthly["MONTH"], rotation=35, ha="right")

ax.tick_params(axis="both", colors=MUTED_COLOR)
ax.grid(axis="y", color=GRID_COLOR, linestyle="--", alpha=0.6)
ax.set_axisbelow(True)

# Format large values into billions for readability
ax.yaxis.set_major_formatter(
    plt.FuncFormatter(lambda value, position: f"{value / 1e9:.0f}B")
)

# Highlight each monthly value
for i, value in enumerate(values):
    ax.annotate(
        f"{value / 1e9:.1f}B",
        (i, value),
        xytext=(0, 13),
        textcoords="offset points",
        ha="center",
        fontsize=9,
        fontweight="bold",
        color=TEXT_COLOR
    )

for spine in ax.spines.values():
    spine.set_color(GRID_COLOR)

ax.legend(
    facecolor=PANEL_COLOR,
    edgecolor=GRID_COLOR,
    labelcolor=TEXT_COLOR
)

ax.margins(y=0.20)
plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "day03_monthly_transaction_value.png",
    dpi=300,
    facecolor=fig.get_facecolor(),
    bbox_inches="tight"
)
plt.close()


# Identify partial month
latest_date = valid_time["INSTANCE_DATE"].max()
latest_month = latest_date.to_period("M")
month_end = latest_month.end_time.date()
is_partial = latest_date.date() < month_end

# Create readable report copy without changing numeric data
monthly_report = monthly.copy()

monthly_report["total_transaction_value"] = (
    monthly_report["total_transaction_value"].map(
        lambda x: f"{x:,.2f}"
    )
)

monthly_report["median_transaction_value"] = (
    monthly_report["median_transaction_value"].map(
        lambda x: f"{x:,.2f}"
    )
)

# Day 3 report
day3_report = [
    "# Day 3: Time-Based Transaction Analysis",
    "",
    "## Objective",
    "Analyze monthly transaction counts and total transaction values.",
    "",
    "## Dataset Overview",
    f"- Total source records: {len(df):,}",
    f"- Records with valid dates and values: {len(valid_time):,}",
    f"- Analysis start date: {START_DATE}",
    f"- Analysis end date: {END_DATE}",
    f"- Earliest date: {valid_time['INSTANCE_DATE'].min()}",
    f"- Latest date: {latest_date}",
    "",
    "## Monthly Results",
    monthly_report.to_string(index=False),
    "",
    "## Key Observations",
    f"- Months analyzed: {len(monthly)}",
    f"- Highest transaction-count month: "
    f"{monthly.loc[monthly['transaction_count'].idxmax(), 'MONTH']}",
    f"- Lowest transaction-count month: "
    f"{monthly.loc[monthly['transaction_count'].idxmin(), 'MONTH']}",
    f"- Highest transaction-value month: "
    f"{monthly.loc[monthly['total_transaction_value'].idxmax(), 'MONTH']}",
    f"- Lowest transaction-value month: "
    f"{monthly.loc[monthly['total_transaction_value'].idxmin(), 'MONTH']}",
    f"- Total transaction records: "
    f"{monthly['transaction_count'].sum():,}",
    f"- Total transaction value: "
    f"{monthly['total_transaction_value'].sum():,.2f}",
    "",
    "## Data Reconciliation",
    f"- Monthly record count: {monthly['transaction_count'].sum():,}",
    f"- Filtered source record count: {len(valid_time):,}",
    "- Monthly count matches filtered source records: "
    f"{monthly['transaction_count'].sum() == len(valid_time)}",
    "",
    "## Data Limitations",
    f"- Latest month is {'partial' if is_partial else 'complete'} "
    f"as of {latest_date.date()}.",
    "- Monthly totals describe recorded transaction values, "
    "not property returns or rental income.",
    "- Transaction counts represent source records; repeated "
    "transaction IDs were retained because their unique-key "
    "meaning has not been confirmed.",
    "- Currency unit has not been independently verified.",
    "",
    "## Output Files",
    "- day03_monthly_summary.csv",
    "- day03_monthly_transaction_count.png",
    "- day03_monthly_transaction_value.png",
]

(OUTPUT_DIR / "day03_time_analysis_report.md").write_text(
    "\n".join(day3_report),
    encoding="utf-8"
)

print("\nMonthly results:")
print(monthly_report.to_string(index=False))

# --------------------------------------------------
# DAY 4: AREA-BASED ANALYSIS
# --------------------------------------------------

# --------------------------------------------------
# DAY 4: AREA-BASED ANALYSIS
# --------------------------------------------------

print("\n========== DAY 4: AREA ANALYSIS ==========")

# Select valid area records
valid_area = df.dropna(
    subset=["AREA_EN", "TRANS_VALUE", "ACTUAL_AREA"]
).copy()

valid_area = valid_area[
    (valid_area["AREA_EN"].astype(str).str.strip() != "")
    & (valid_area["TRANS_VALUE"] > 0)
    & (valid_area["ACTUAL_AREA"] > 0)
].copy()

# Calculate price per square metre
valid_area["PRICE_PER_SQM"] = (
    valid_area["TRANS_VALUE"] / valid_area["ACTUAL_AREA"]
)

# Calculate transaction count for each area
area_count = (
    valid_area.groupby("AREA_EN")
    .size()
    .rename("transaction_count")
    .reset_index()
)

# Calculate median price per square metre
area_price = (
    valid_area.groupby("AREA_EN")
    .agg(
        median_price_per_sqm=("PRICE_PER_SQM", "median"),
        valid_price_records=("PRICE_PER_SQM", "count"),
    )
    .reset_index()
)

# Combine metrics
area_summary = area_count.merge(
    area_price,
    on="AREA_EN",
    how="inner"
)

area_summary = area_summary.sort_values(
    "transaction_count",
    ascending=False
)

# Save complete area summary
area_summary.to_csv(
    OUTPUT_DIR / "day04_area_summary_all.csv",
    index=False
)

# Select Top 10 Areas by Transaction Count
top_count = area_summary.head(10).copy()

# Premium Top 10 Areas by Transaction Count Chart
fig, ax = plt.subplots(figsize=(13, 8))
fig.patch.set_facecolor(BG_COLOR)
ax.set_facecolor(PANEL_COLOR)

plot_count = top_count.sort_values(
    "transaction_count",
    ascending=True
)

bars = ax.barh(
    plot_count["AREA_EN"],
    plot_count["transaction_count"],
    color=PURPLE,
    edgecolor=BLUE,
    linewidth=1.3,
    height=0.65
)

ax.set_title(
    "Top 10 Areas by Transaction Count",
    fontsize=19,
    fontweight="bold",
    color=TEXT_COLOR,
    pad=24
)

ax.set_xlabel(
    "Number of Transaction Records",
    fontsize=12,
    color=TEXT_COLOR,
    labelpad=12
)
ax.set_ylabel("Area", fontsize=12, color=TEXT_COLOR, labelpad=12)

ax.tick_params(axis="both", colors=MUTED_COLOR)
ax.grid(axis="x", color=GRID_COLOR, linestyle="--", alpha=0.6)
ax.set_axisbelow(True)

for bar in bars:
    width = bar.get_width()
    ax.annotate(
        f"{width:,.0f}",
        (width, bar.get_y() + bar.get_height() / 2),
        xytext=(8, 0),
        textcoords="offset points",
        va="center",
        fontsize=9,
        fontweight="bold",
        color=TEXT_COLOR
    )

for spine in ax.spines.values():
    spine.set_color(GRID_COLOR)

ax.margins(x=0.18)
plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "day04_top_areas_by_count.png",
    dpi=300,
    facecolor=fig.get_facecolor(),
    bbox_inches="tight"
)
plt.close()

# Suppress small samples for price comparison
reliable_areas = area_summary[
    area_summary["valid_price_records"] >= MIN_AREA_TRANSACTIONS
].copy()

top_price = reliable_areas.sort_values(
    "median_price_per_sqm",
    ascending=False
).head(10)

# Premium Top 10 Areas by Median Price per Sqm Chart
fig, ax = plt.subplots(figsize=(13, 8))
fig.patch.set_facecolor(BG_COLOR)
ax.set_facecolor(PANEL_COLOR)

plot_price = top_price.sort_values(
    "median_price_per_sqm",
    ascending=True
)

bars = ax.barh(
    plot_price["AREA_EN"],
    plot_price["median_price_per_sqm"],
    color=BLUE,
    edgecolor=PURPLE,
    linewidth=1.3,
    height=0.65
)

ax.set_title(
    "Top 10 Areas by Median Price per Sqm",
    fontsize=19,
    fontweight="bold",
    color=TEXT_COLOR,
    pad=24
)

ax.set_xlabel(
    "Median Price per Sqm (Source Units)",
    fontsize=12,
    color=TEXT_COLOR,
    labelpad=12
)
ax.set_ylabel("Area", fontsize=12, color=TEXT_COLOR, labelpad=12)

ax.tick_params(axis="both", colors=MUTED_COLOR)
ax.grid(axis="x", color=GRID_COLOR, linestyle="--", alpha=0.6)
ax.set_axisbelow(True)

for bar in bars:
    width = bar.get_width()
    ax.annotate(
        f"{width:,.2f}",
        (width, bar.get_y() + bar.get_height() / 2),
        xytext=(8, 0),
        textcoords="offset points",
        va="center",
        fontsize=9,
        fontweight="bold",
        color=TEXT_COLOR
    )

for spine in ax.spines.values():
    spine.set_color(GRID_COLOR)

ax.margins(x=0.22)
plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "day04_median_price_per_sqm.png",
    dpi=300,
    facecolor=fig.get_facecolor(),
    bbox_inches="tight"
)
plt.close()

# Create readable copies for Day 4 report
top_count_report = top_count.copy()
top_count_report["median_price_per_sqm"] = (
    top_count_report["median_price_per_sqm"].map(
        lambda x: f"{x:,.2f}"
    )
)

top_price_report = top_price.copy()
top_price_report["median_price_per_sqm"] = (
    top_price_report["median_price_per_sqm"].map(
        lambda x: f"{x:,.2f}"
    )
)

# Day 4 report
day4_report = [
    "# Day 4: Area-Based Transaction Analysis",
    "",
    "## Objective",
    "Compare areas using transaction counts and median price per sqm.",
    "",
    "## Dataset Overview",
    f"- Total source records: {len(df):,}",
    f"- Records eligible for area analysis: {len(valid_area):,}",
    f"- Distinct areas analyzed: {area_summary['AREA_EN'].nunique():,}",
    "",
    "## Top 10 Areas by Transaction Count",
    top_count_report.to_string(index=False),
    "",
    "## Top 10 Areas by Median Price per Sqm",
    top_price_report.to_string(index=False),
    "",
    "## Methodology",
    "- Individual price per sqm = TRANS_VALUE / ACTUAL_AREA.",
    "- Area-level price is the median of individual price-per-sqm values.",
    f"- Areas with fewer than {MIN_AREA_TRANSACTIONS} valid records "
    "are excluded from the price comparison chart.",
    "- The 30-record threshold is an analysis choice to reduce "
    "the influence of very small samples; it is not an official source rule.",
    "- The area summary CSV retains all eligible areas.",
    "- Original source records are not modified.",
    "",
    "## Limitations",
    "- Small samples can produce unstable area comparisons.",
    "- ACTUAL_AREA is used because it was valid and positive "
    "for all records in the earlier data-quality checks.",
    "- Currency unit has not been independently verified.",
    "- Transaction values do not establish rental yield or investment returns.",
    "",
    "## Output Files",
    "- day04_area_summary_all.csv",
    "- day04_top_areas_by_count.png",
    "- day04_median_price_per_sqm.png",
]

(OUTPUT_DIR / "day04_area_analysis_report.md").write_text(
    "\n".join(day4_report),
    encoding="utf-8"
)

print("\nTop 10 areas by transaction count:")
print(top_count_report.to_string(index=False))

print("\nTop 10 areas by median price per sqm:")
print(top_price_report.to_string(index=False))

print("\n========== ANALYSIS COMPLETED ==========")
print(f"All output files saved in: {OUTPUT_DIR}")
print("Original source CSV files were not modified.")
