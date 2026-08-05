# 01 - Establish the SMAIRT Lab baseline

**What to build:** Rename the distribution and command to `smairt-lab` so it installs beside
upstream `smairt`, moving the package to `src/smairt_lab/` and updating pyproject, CI gate
commands, smoke-install artifact names, and every generated reference; then fix the two
defects that would otherwise corrupt every downstream issue: align the contract's
`scaffold_version` default with the package version so a freshly generated project does not
immediately fail its own Project Check and become ineligible for repair and capability
changes, and make `phase_directories()` honour its argument instead of discarding it and
always returning the synthetic tuple. Regenerate goldens as one reviewed commit.

**Blocked by:** None - can start immediately.

**Status:** ready-for-agent

- [ ] `uv tool install .` provides `smairt-lab` and does not shadow an installed `smairt`.
- [ ] A freshly generated project reports no issues from `smairt-lab check`.
- [ ] `scaffold_version` in a new contract equals the installed package version.
- [ ] `phase_directories()` returns the directories for the phase it is given.
- [ ] A test asserts a new project's `scaffold_version` matches the package version.
- [ ] A test asserts `phase_directories()` differs across the three phases.
- [ ] Goldens are regenerated and the diff is limited to the rename and the two fixes.
- [ ] Every release gate in the CI workflow passes on the renamed package.
