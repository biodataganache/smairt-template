# Rewrite the README as the single front door

Type: task
Status: resolved
Blocked by: 05, 10, 11, 12, 13, 14

## Question

Can a first-time researcher understand what SMAIRT is, install it from the repository, create a valid project in about one minute, and know exactly where to go next without reading another introduction?

## Work

- Implement the information shape decided in “Design one newcomer path and a smaller documentation hierarchy.”
- Lead with the framework's current value and generated-project model, not migration history or internal vocabulary.
- Include one tested installation path, one tested first-project path, supported Python versions, preview/release status, and concise Paper/HPC positioning.
- Point to the rewritten demos as scientific evidence and examples, and to `docs/` for depth.
- Keep legacy Cookiecutter history to one clear pointer. Move contributor and upgrade detail out of the first-use path.
- Verify every command from a clean clone of the branch, not from the development environment that produced it.

## Resolution

Resolve when the README is the only required newcomer introduction, its commands pass from a clean clone, all links resolve, and it does not duplicate tutorial bodies.

## Resolved

The README already had the right shape from ticket 07. What this ticket added was the verification
it actually asks for — every command from a clean clone rather than from the development
environment — and that found a real defect.

`git clone`, then `uv tool install .`, then the documented loop run with the `python3` the README
tells the reader to use: the first two commands died with `ModuleNotFoundError: No module named
yaml`. `new_track.py` and `new_iteration.py` imported PyYAML at module scope while using it only for
optional rigor declarations that already degrade gracefully. The tool ships its own environment, so
`smairt new` worked and the failure appeared only after project creation, on a machine whose system
interpreter lacks PyYAML. Fixed by making the import optional; scaffold bumped to 0.5.1 because two
tool-owned files changed content.

Also corrected the Examples section, which still said the demos were being rewritten and gave no way
to tell which were current. It now names the three current demos with a reason to pick each and
points at the taxonomy for the rest.

Verified from a clean clone: install, guided and flag-driven creation, the full loop under a bare
`python3`, check, repair, upgrade, open, and both capability enables. All README links resolve.
