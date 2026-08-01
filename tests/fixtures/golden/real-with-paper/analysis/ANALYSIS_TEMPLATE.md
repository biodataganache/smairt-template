# Analysis [XX] - [Brief Title]

## Executive Summary

[Summarize what was tested, what happened, and the main takeaway in two or three sentences.]

## Experiment Details

- **Script**: `experiments/XX_phase/script_XX_description.py`
- **Hypothesis**: `hypotheses/HYPOTHESIS_XX.md`
- **Log**: `results/logs/script_XX_*.log`
- **Phase**: synthetic | downloaded | real
- **Data record**: `data/[phase]/README.md`

## Key Results

[Present the important findings, including uncertainty and negative results.]

| Metric | Expected | Observed | Assessment |
|---|---:|---:|---|
| [Metric 1] | [Prediction] | [Result] | Supported / Not supported |
| [Metric 2] | [Prediction] | [Result] | Supported / Not supported |

## Hypothesis Assessment

### SUPPORTED | REFUTED | PARTIALLY SUPPORTED | INCONCLUSIVE

[Explain how the evidence changes confidence in the stated hypothesis.]

### Where It Works

- [Condition or parameter range where the approach succeeds]
- [Evidence supporting that boundary]

### Where It Breaks Down

- [Failure condition or edge case]
- [Evidence and possible explanation]

## Comparison to Prior Work

| Comparison | Previous result | Current result | Interpretation |
|---|---:|---:|---|
| [Metric or behavior] | [Value] | [Value] | [Change and meaning] |

## Limitations

- [Data limitation]
- [Method or model limitation]
- [Uncertainty, confounding, or generalization limit]

## Implications

[Explain what this result means for the broader research question.]

## Decision

CONTINUE | REVISE | PIVOT | STOP

[State why this decision follows from the evidence.]

## Next Steps

1. [Most informative follow-up]
2. [Alternative explanation to test]
3. [Validation or robustness check]

## Files Generated

- `results/logs/script_XX_*.log` - complete execution record
- `results/figures/[figure]` - visualization and provenance
- [Other result tables or summaries]

## Intellectual Contribution Notes

[Record important researcher choices or interpretations in
`prompts/intellectual_contribution.md` and link the relevant entry.]
