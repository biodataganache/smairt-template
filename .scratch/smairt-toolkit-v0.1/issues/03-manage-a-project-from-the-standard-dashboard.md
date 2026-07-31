# 03 - Manage a project from the Standard dashboard

**What to build:** Deliver a useful bare `smairt` Home and Standard Mode project dashboard. Users can create/open/reopen projects, launch or receive guidance for their selected assistant, edit safe project metadata and collaborators, change a license through a guarded flow, enable or non-destructively deactivate Paper/HPC support, run Project Check, and select previewed safe repairs without the dashboard conducting research.

**Blocked by:** 02 - Guide project creation in the TUI.

**Status:** done

- [x] Home detects the current project and otherwise offers Create New Project, Recent Projects, Open Existing Project, Help, and Exit.
- [x] Recent Projects stores at most ten local paths/timestamps and removes missing paths quietly.
- [x] Standard Mode exposes assistant launch/open, Project Settings, Paper Support, HPC Support, Project Check, Help, and Exit.
- [x] Project Settings edits approved metadata, collaborators, assistant, current phase, capabilities, license, experience preference, and motion preference while keeping slug/folder immutable.
- [x] Assistant aliases and launch commands follow verified current conventions; unavailable tools produce guidance and a folder-opening fallback without automatic installation.
- [x] Paper/HPC enable, disable, and re-enable operations are idempotent and preserve retained artifacts and researcher modifications.
- [x] License changes warn, preview, confirm, and refuse to replace modified legal text.
- [x] Project Check reports only structural/configuration issues in human-readable and JSON forms with stable exit behavior.
- [x] Safe repairs are selectable, previewed, explicitly confirmed, and never overwrite or delete scientific content.
- [x] Public CLI commands for open, check, Paper enable/disable, and HPC enable/disable match dashboard behavior.
- [x] Input-driven and command-level tests cover Home, recents, settings, capabilities, assistants, license safety, checks, and repairs.
