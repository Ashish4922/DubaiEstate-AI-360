# GenAI Day 6: Market-Summary Report

**Domain:** GenAI | **Week:** 1 | **Day:** 6

## Approach
`report.py` runs the Day 3 retrieval tools and writes Markdown. No figure is
typed by hand, so the report can be regenerated if the data changes.

## Citations
- `[A#]` points to an aggregate: the tool call, filters, sample size and date coverage.
- `[R#]` points to a specific transaction (number, date, value) that can be found in the CSV.
- Section 8 lists every reference.

## What the report contains
Dataset overview and data quality, monthly sales, top areas, off-plan share,
median price per sq m (units only), example transactions, limitations.

## Checks performed
- pytest checks that every citation is defined, the row count matches, the
  partial month is labelled and no forward-looking language appears.
- Manual check: [write which figures you verified against the CSV and what you found].

## Limitations
- Only descriptive statistics. No causes, trends beyond counts, or outlook.
- Area-level medians depend on sample size; small ones are flagged.
- Duplicate transaction numbers with conflicting data are kept and disclosed.
- Template-generated text: no LLM was used, so no data left the machine.