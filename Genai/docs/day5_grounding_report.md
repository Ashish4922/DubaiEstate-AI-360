# GenAI Day 5: Grounding Tests

**Domain:** GenAI | **Week:** 1 | **Day:** 5

## 1. What "grounded" means here
Every figure in an answer must come from a verified result computed by
`retrieval.py`. `grounding.py` checks this by extracting the numbers from the
answer and confirming each one appears in the result behind it.

## 2. Test coverage
| Area | What is tested | Where |
|---|---|---|
| Numerical correctness | Medians, price per sq m, counts and shares match hand calculations and an independent pandas calculation on the real CSVs | Sections A, B |
| Unknown questions | Jokes, weather, ranking by price, "best returns" are refused | Section C |
| Missing data | Unknown area, no matching rows, small sample, partial month | Section C |
| Malformed input | Empty, symbols, SQL text, non-English, very long, None | Section C |
| Hallucination resistance | Injection attempts refused; injected figures never reach an answer | Section D |
| Loader robustness | Exact duplicates, conflicting duplicates, zero values, missing file, bad headers | Section E |

## 3. Results
- `python -m pytest genai/tests -v`: [paste your real result, e.g. "NN passed"]
- `python -m genai.grounding_report`: [paste your real result, e.g. "0 failures"]

## 4. Findings
[Write what you actually observed. Examples of what to look for:]
- Did any question get routed to the wrong tool?
- Did any test fail at first? What did it show, and how was it fixed?
- Duplicate audit on the real data: [paste the exact_duplicates_removed and
  duplicate_keys_with_different_data lines from `python -m genai.demo_retrieval`]

## 5. Limitations
- Safety and routing use keyword rules, so rephrased questions can slip
  through or be refused wrongly. The grounding check limits the damage,
  because answers can only contain computed figures.
- `grounding.py` checks the figure block only, not dates or warning text.
- Template mode has no LLM, so these tests do not measure LLM hallucination.
  If an LLM is added later, the same checker can validate its output.
- Tests run on a snapshot (data to 2026-10-29). A refreshed dataset may need
  expected values updated.
- The 30-row minimum sample is a project convention, not a statistical rule.