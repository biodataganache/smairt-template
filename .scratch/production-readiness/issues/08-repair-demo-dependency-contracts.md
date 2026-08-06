# Repair demo dependency contracts

Type: task
Status: unclaimed
Blocked by: 02

## Question

Can each demo install exactly the dependencies needed to run its scientific scripts, with optional heavyweight work clearly separated from the default path?

## Work

- Add or remove the undeclared `seaborn` dependency in proteomics differential expression.
- Add or remove the undeclared `scikit-learn` dependency in the PPI network demo.
- Preserve the protein-properties scientific calculator implementation behind a clear module interface; do not overwrite the current scaffold's `scripts.shared` logging interface with a legacy copy.
- Decide how protein LM declares PyTorch and optional `fair-esm`, including first-run model-weight download and an offline/default path.
- Replace nine ad hoc dependency stories with one documented demo-environment convention where practical. Do not introduce a package-manager adapter unless there are two real variants at the seam.
- Verify clean environment installation and imports for every demo before scientific reruns begin.

## Resolution

Resolve when each demo's dependency declaration is complete, minimal, reproducible, and tested from an empty environment, with optional model downloads explicit rather than surprising.
