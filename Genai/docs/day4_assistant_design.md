# GenAI Day 4: Assistant Prototype

**Domain:** GenAI | **Week:** 1 | **Day:** 4

## Design
Template mode. Python selects a retrieval tool, the tool computes a verified
result, and the answer text is generated from that result. No LLM or network
call is used, so no dataset content leaves the machine. The Day 2 prompt is
still built for each answer (`Answer.prompt`) so an LLM can be added later.

## Flow
question -> safety checks -> tool selection -> retrieval tool ->
verified result -> answer text

## Safety checks (run first)
| Check                                          | Result                         |
|------------------------------------------------|--------------------------------|
| Instruction to change rules (prompt injection) | Refused                        |
| Buy / sell / invest advice                     | Refused                        |
| Prediction or forecast                         | Refused                        |
| Rent, yield, occupancy, maintenance            | Refused                        |
| Unrecognised question                          | Refused with example questions |

## Tool selection
| Question wording                         | Tool                  |
|------------------------------------------|-----------------------|
| "each month", "monthly"                  | monthly_sales_count   |
| "off-plan", "ready"                      | offplan_share         |
| "compare", "between" + areas or per sq m | compare_price_per_sqm |
| "top", "busiest"                         | top_areas_by_count    |
| "per sq m"                               | median_price_per_sqm  |
| "median", "price", "value"               | median_sale_value     |

## Every answer includes
Figure, unit, filters, sample size, date coverage, warnings and an
uncertainty note.

## Known limitations
- Tool selection uses keyword rules, so unusual wording may be refused.
- Area names must match the dataset spelling closely (suggestions are
  shown when an area is not found).
- "Average" questions are answered with the median, and the answer says so.
- Comparison is price per sq m for Unit-type sales only.
- Ranking areas by price is not supported yet.
- Day 5 tests numerical correctness more deeply.