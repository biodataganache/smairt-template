# 04 - Expose Advanced project controls

**What to build:** Add Advanced Mode as a per-project local interface preference that retains every Standard action while exposing deeper inspection, verbose diagnostics, safe managed-asset regeneration, explicit convention customization, and detected local tool information. Keep the boundary safe: no arbitrary configuration editor, shell, integrations, or fork scientific engine.

**Blocked by:** 03 - Manage a project from the Standard dashboard.

**Status:** ready-for-agent

- [ ] Users can switch between Standard Mode and Advanced Mode in Settings and the choice remains local to that project checkout.
- [ ] Advanced Mode retains all Standard Mode actions and adds full project-contract inspection.
- [ ] Managed-file ownership and hashes are inspectable without exposing confusing implementation noise by default.
- [ ] Verbose Project Check explains each diagnostic and its affected artifact.
- [ ] Users can preview and regenerate only missing or unmodified managed guidance/templates.
- [ ] Explicit settings support the agreed prompt/code-convention customization without arbitrary YAML editing.
- [ ] Detected Python, Git, and selected-assistant executable paths are visible.
- [ ] Advanced Mode does not expose arbitrary shell commands, API keys, integrations, safety/provenance engines, or scientific workflow operations.
- [ ] Navigation, persistence, inspection, regeneration safety, and customization behavior are covered through public TUI/CLI seams.
