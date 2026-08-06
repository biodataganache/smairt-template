# Open and land the main-branch pull request

Type: task
Status: unclaimed
Blocked by: 16

## Question

Can this branch replace `main` through a reviewable pull request with authoritative CI evidence and a reversible release decision?

## Work

- Inspect branch status, the complete diff from `origin/main`, all included commits, repository remotes, and the final support/release notes before opening the pull request.
- Explain the migration from cookiecutter template to installed framework, the generated-project compatibility story, demo rewrites, legacy location, upgrade safety, and verification evidence.
- Let the pull request run the authoritative GitHub Actions matrix on Ubuntu and macOS with Python 3.11, 3.12, and 3.13. Fix failures with new commits; do not bypass checks.
- Obtain the required human and organizational approvals before merge.
- Decide explicitly whether merge also authorizes changing `## Unreleased` to a dated `0.4.0` release and creating tag `v0.4.0`; do not infer release authorization from merge authorization.
- After merge, test the README's default-branch clone/install path against the real remote and verify GitHub metadata, license detection, and links.

## Resolution

Resolve when the pull request is merged to `main`, required checks and reviews are green, the documented default-branch installation works, and the release/tag decision is recorded without ambiguity.
