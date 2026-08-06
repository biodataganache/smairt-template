# Rewrite the README as the single front door

Type: task
Status: unclaimed
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
