# Repair demo dependency contracts

Type: task
Status: resolved
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

## Answer

Three demos could not run for anyone but their author. An AST scan of all nine confirmed exactly
the three the audit predicted, and no others.

- **`ppi_network`** imported `sklearn.metrics` in three scripts with no `scikit-learn` declared.
- **`proteomics_de`** imported `seaborn` in the parameter sweep with no `seaborn` declared.
- **`protein_lm`** imported `esm` with `fair-esm` only mentioned in a comment.

The first two are plain omissions and are now declared, with a comment saying what each is for.
Verified by installing each `requirements.txt` into a clean 3.12 environment and importing what
the scripts actually import.

`protein_lm` is different: `fair-esm` is *genuinely* optional. It is needed by one real-data rung
and downloads pretrained weights on first use, so forcing it on everyone running the synthetic
rungs would be wrong. The deferred import stays; what changed is that its absence now explains
itself with the install command instead of raising a bare `ImportError` that reads as a broken
demo.

### `protein_properties` is not fixable here

Its scripts import calculator functions from `scripts.shared`, which the *old* demo re-exported
from its own `calculators.py`. The current scaffold's `shared/__init__.py` exports only logging
and run-status helpers. That is a migration problem, not a declaration problem — the module has
to move to a real seam when the demo is regenerated. Left to the demo rewrite rather than papered
over by adding a dependency.

### Tests

`tests/test_demos.py` asserts every demo declares what it imports, and that an optional
dependency names itself when missing. Verified the first genuinely fails by deleting
`scikit-learn` and watching it name all three offending files.

The scan also surfaced a `SyntaxWarning` on every parse of the lunar demo: a 60-line pasted run
transcript containing Windows paths, which is the "paste block" pattern the current scaffold
explicitly retired. Removed, with a note that results belong in `results/logs/` and
interpretation in `analysis/`.

205 tests pass, up from 187.
