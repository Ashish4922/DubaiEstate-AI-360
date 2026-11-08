# Day 5: GenAI Grounding Tests

## Objective

Validate that the GenAI assistant produces accurate, dataset-grounded responses and avoids unsupported claims.

## Test Coverage

### 1. Numerical Correctness
Verified that the assistant returns transaction count, total transaction value, and average transaction value using the exact retrieved metrics.

### 2. Unsupported Questions
Verified that the assistant rejects questions outside its supported transaction-metrics scope.

### 3. Unknown Areas
Verified that unknown area names are rejected instead of silently returning dataset-wide statistics.

### 4. Missing Data
Verified that the assistant reports when no matching transactions are found and does not fabricate numerical results.

### 5. Hallucination Resistance
Tested questions involving guaranteed investment returns and property price predictions. The assistant rejects these unsupported investment claims.

## Validation

Command:

```bash
python -m pytest tests/test_genai_assistant.py tests/test_genai_data_retrieval.py -v
```

Result: 10 tests passed.

## Limitations

- The assistant supports transaction count, total transaction value, and average transaction value.
- Rental yield, occupancy, maintenance costs, and guaranteed investment returns are not supported.
- Tests use mocked retrieval metrics for assistant grounding scenarios.
- Results are based on the available Dubai transaction dataset and do not constitute investment advice.

## Conclusion

The grounding tests verify numerical consistency, handling of unsupported questions, missing-data behavior, and resistance to unsupported investment claims.
