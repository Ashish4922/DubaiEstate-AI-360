# GenAI: Property-Information Assistant (Week 1)

A prototype assistant that answers questions about 2026 Dubai property
transactions. Every figure is computed by Python from the project CSVs. No
LLM or external API is used, so no dataset content leaves the machine.

This is a learning prototype, not an investment advisory system.

## Flow
question -> safety checks -> tool selection -> retrieval tool ->
verified result -> answer text

## Project structure
| Path | Purpose |
|---|---|
| `retrieval.py` | CSV loader with validation and duplicate audit; deterministic tools |
| `prompts.py` | System, answer and refusal prompt templates; verified-result format |
| `assistant.py` | Safety checks, tool selection, answer writing |
| `chat.py` | Command-line interface |
| `grounding.py` | Checks that every figure in an answer exists in its verified result |
| `grounding_report.py` | PASS/FAIL table on the real dataset |
| `report.py` | Market-summary generator with citations |
| `reports/` | Generated market-summary draft |
| `tests/` | pytest tests (synthetic data, plus real-data checks) |
| `docs/` | Design notes for each day, including the five test cases |
| `inspect_data.py`, `profile_data.py` | Day 1 data inspection scripts |

## Setup
From the repository root (Python 3.10 or newer):

    python -m venv .venv
    .venv\Scripts\Activate.ps1
    pip install -r genai/requirements.txt

The CSV files must be in `DataSets/`. They are only read, never modified.

## Usage
    python -m genai.chat
    python -m genai.chat "Which are the top 5 areas by number of sales?"
    python -m genai.chat --show-prompt "What is the median price of flats?"
    python -m genai.report
    python -m genai.grounding_report
    python -m pytest genai/tests -v

## What the assistant answers
Monthly sales counts, top areas by number of sales, off-plan versus ready
share, median sale value, median price per sq m (unit-type sales only) and
two-area comparisons.

It refuses predictions, buy/sell/invest advice, rent/yield/occupancy
questions and attempts to change its rules.

## Dataset audit
- Rows loaded: [from section 1 of the report]
- Exact duplicate rows removed: [from the report]
- Transaction numbers repeated with different data (kept): [from the report]
- Invalid rows removed: [from the report]
- Date coverage: 2026-01-01 to 2026-10-29 (October is a partial month)

## Test results
- `python -m pytest genai/tests -v`: [your real summary line]
- `python -m genai.grounding_report`: [your real result]

## Known limitations
- Tool selection and safety checks use keyword rules, so unusual wording may
  be refused or misrouted. The grounding check limits the damage because
  answers can only contain computed figures.
- Template mode has no LLM, so the tests do not measure LLM hallucination.
- Price per sq m uses Unit-type sales only. Land and Building are excluded.
- Subtype labels in the source are inconsistent and some are blank.
- Samples under 30 rows are flagged unreliable (a project convention, not a
  statistical rule).
- Some transaction numbers repeat with different data. Both rows are kept
  because the correct one cannot be determined.
- The dataset has no rent, yield, occupancy or maintenance fields.
- Area names must closely match the dataset spelling.
- Figures describe historical transactions only. Not investment advice.

## Daily summary
| Day | Deliverable |
|---|---|
| 1 | Data inspection, five grounded questions, prohibited behaviours |
| 2 | Prompt templates and verified-result format |
| 3 | Retrieval tools, loader, duplicate audit, tests |
| 4 | Assistant prototype with safety checks, CLI |
| 5 | Grounding checker, hallucination and robustness tests |
| 6 | Market-summary report with citations |
| 7 | Final package, five test cases, documentation |