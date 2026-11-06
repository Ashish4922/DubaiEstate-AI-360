# GenAI: Property Information Assistant (Week 1)

## Day 1 completed
- Inspected both CSV files (22 columns each, 134,185 rows combined)
- Profiled date coverage (2026-01-01 to 2026-10-29), categories and duplicates
- Defined five grounded user questions and prohibited behaviours
  (To check `docs/day1_use_cases.md`)
## Run
    pip install pandas
    python genai/inspect_data.py
    python genai/profile_data.py

## Day 2 completed
- Prompt templates in `prompts.py` (system, answer, refusal)
- Verified-result format with required-field check
- Design notes in `docs/day2_prompt_design.md`
## Run 
    python -m genai.demo_prompts

## Day 3 completed
- `retrieval.py`: loader with header validation and duplicate audit, plus
  deterministic tools (monthly count, median value, median price per sq m,
  area comparison, top areas, off-plan share)
- Exact duplicate rows are dropped; same-ID rows with different data are kept
  and reported
- Price per sq m uses Unit-type sales only
- Samples under 30 and partial months are flagged in `warnings`
## Run
    python -m genai.demo_retrieval
    python -m pytest genai/tests -v

## Day 4 completed
- `assistant.py`: question -> safety checks -> tool selection -> verified
  result -> answer text (template mode, no external API)
- `chat.py`: command-line interface
- Refuses predictions, investment advice, rent/yield questions and prompt
  injection
- Design notes in `docs/day4_assistant_design.md`
## Run
    python -m genai.chat
    python -m genai.chat "Which are the top 5 areas by number of sales?"
    python -m pytest genai/tests -v