# 04 - Expose Advanced project controls

**What to build:** Add Advanced Mode as a per-project local interface preference that retains every Standard action while exposing deeper inspection, verbose diagnostics, safe managed-asset regeneration, explicit convention customization, and detected local tool information. Keep the boundary safe: no arbitrary configuration editor, shell, integrations, or fork scientific engine.

**Blocked by:** 03 - Manage a project from the Standard dashboard.

**Status:** done

- [x] Users can switch between Standard Mode and Advanced Mode in Settings and the choice remains local to that project checkout.
- [x] Advanced Mode retains all Standard Mode actions and adds full project-contract inspection.
- [x] Managed-file ownership and hashes are inspectable without exposing confusing implementation noise by default.
- [x] Verbose Project Check explains each diagnostic and its affected artifact.
- [x] Users can preview and regenerate only missing or unmodified managed guidance/templates.
- [x] Explicit settings support the agreed prompt/code-convention customization without arbitrary YAML editing.
- [x] Detected Python, Git, and selected-assistant executable paths are visible.
- [x] Advanced Mode does not expose arbitrary shell commands, API keys, integrations, safety/provenance engines, or scientific workflow operations.
- [x] Navigation, persistence, inspection, regeneration safety, and customization behavior are covered through public TUI/CLI seams.
