# 03 - Carry a set of assistants in one project

**What to build:** Change the contract's single `assistant` to a non-empty, order-preserving,
deduplicated `assistants` list so one project can serve a team that mixes harnesses, migrating a
scalar value to a single-element list on load so every existing contract keeps working and no
assistant is removed from the enum. Render an activator for every selected assistant at
generation and when the selection changes, report the artifacts belonging to a deselected
assistant without deleting them, and update the wizard, settings, dashboard, check, and launch
paths to operate on a set while keeping launch a single deliberate choice.

**Blocked by:** 02 - Generate harness files each assistant actually loads.

**Status:** ready-for-agent

- [ ] A project can be created with several assistants and receives one activator for each.
- [ ] A contract holding a scalar `assistant` loads and migrates to a single-element list.
- [ ] A contract holding a retired assistant such as `pi` still loads.
- [ ] Adding an assistant later creates only its missing activator.
- [ ] Deselecting an assistant reports its artifacts and deletes nothing.
- [ ] `smairt-lab check` requires a loadable artifact for every selected assistant.
- [ ] The wizard offers assistants as checkboxes with a visible `Next →` row.
- [ ] Goldens gain a multi-assistant case.
