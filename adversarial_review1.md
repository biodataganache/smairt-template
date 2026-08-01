# Adversarial Review 1

## Scope

This review challenged the V0.1 CLI migration against clone safety, scientific
workflow continuity, capability semantics, legal choices, legacy isolation,
and the truthfulness of public guidance.

## Critical Findings

1. `.smairt/managed-files.yaml` was ignored by Git while serving as the only
   source of managed hashes and regeneration content. Clones therefore could
   not check, inspect, or regenerate projects.
2. Empty phase directories disappeared after clone. Tracked phase README files
   are required for a durable research layout.
3. The migration removed the practical hypothesis-to-script-to-log workflow,
   including script creation and dual terminal/file logging.
4. `starting_phase` was mutated as the project advanced, destroying provenance.
   The contract needs immutable `starting_phase` and mutable `current_phase`.
5. Paper and HPC deactivation changed only metadata. Checks and regeneration
   continued to present retained capability files as active guidance.

## Important Findings

1. A researcher filling `paper/outline.md` caused a managed-file failure even
   though editing the outline is its intended use.
2. Custom wizard domains could trap Back navigation because retained free text
   was not a valid menu value.
3. Noninteractive generation selected MIT by default without an explicit legal
   acknowledgement.
4. Recent projects were validated only as directories, not SMAIRT projects.
5. `check` used the same exit status for project issues and an invalid project
   path.
6. Zoo Code had no generated pointer to the canonical assistant context.
7. Active docs, skills, demos, CI, and package metadata still described the
   removed Cookiecutter workflow and other nonexistent tooling.

## Recovery Decisions

- Derive managed asset content and expected hashes from the installed package
  plus tracked `smairt.yaml`; do not duplicate full asset content in a project
  manifest.
- Compare `scaffold_version` with the installed package and report mismatches
  without inventing historical package assets.
- Restore corrected workflow assets: phase guidance, `new_script.py`,
  `TeeLogger`, known patterns, context index, contribution record, twelve-step
  loop, and philosophy.
- Keep Paper as an integrated optional overlay. Disable is non-destructive;
  inactive capability assets are not checked or regenerated until re-enabled.
- Treat the Paper outline as a researcher-editable starter.
- Make the installed `smairt` command the only supported generator.
- Preserve the current Cookiecutter adapter and the complete template from
  commit `78f22af` under `legacy/cookiecutter/` as unsupported reference
  material, including documented historical defects.
- Retire browser-paste context compilation, session compilation, the broken
  historical paper iteration engine, duplicate paper draft layouts, and
  operational claims for integrations that do not exist.

## Verification Requirements

- Exercise behavior through the installed `smairt` command.
- Verify a Git clone can check and inspect without local ignored bookkeeping.
- Verify generated phase directories survive through tracked guidance.
- Verify enabled, inactive, and re-enabled capability behavior preserves work.
- Run formatting, lint, strict type checking, the full tests, package builds,
  and isolated wheel and source-distribution smoke tests.
