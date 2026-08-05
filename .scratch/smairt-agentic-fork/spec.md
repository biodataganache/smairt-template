# SMAIRT Lab: Machine-Legible Provenance Across Harnesses

Status: ready-for-agent

## Problem Statement

SMAIRT's research loop is sound and its division of labour is defensible. Recent
published evidence supports it directly: an ablation across seven human-in-the-loop
regimes found that targeted intervention at a small number of high-leverage decision
points scored 7.27/10 with an 87.5% accept rate, against 4.03 and 25% for full autonomy
and 5.19 and 50% for approval at every step. SMAIRT already places researcher judgment
at those points. The loop does not need replacing.

What the loop lacks is machine legibility. Every guarantee SMAIRT offers today is prose
addressed to a human. Nothing an assistant writes is mechanically checked against
evidence, so a fabricated number and a measured one are indistinguishable in an analysis
file. Nothing binds a citation to a paper that exists. The lesson store grows without
bound and without retrieval. The decisions the researcher owns are described in a
document rather than named, so an assistant cannot be asked to stop at one.

Harness integration is worse than incomplete; it is silently wrong. The tool writes one
identical pointer file for each of six assistants. Two of those pointers are never loaded
by the assistant they target. `ZOO.md` is not a path Zoo Code reads: Zoo Code reads
`.roo/rules/`, `.roorules`, and `AGENTS.md`. A `.mdc` file without frontmatter is a manual
Cursor rule that stays dormant until it is @-mentioned. In both cases Project Check
reports the pointer as healthy, because it tests only that the file exists. A researcher
who selects Zoo Code or Cursor today receives a file their assistant ignores and a tool
that tells them everything is fine.

Compounding this, the contract holds a single assistant, and switching leaves the previous
harness's file behind. Research teams routinely mix harnesses on one repository, and
SMAIRT cannot express that.

## Solution

SMAIRT Lab is an additive fork that makes the existing loop checkable without changing
who decides anything. It adds no stage to the twelve steps and no autonomy to the tool.

Harness support becomes descriptor-driven. One `harnesses.yaml` declares, per assistant,
the project artifact the assistant actually reads, the body format that makes it load, and
whether the assistant reads `AGENTS.md`. `AGENTS.md` becomes the shared spine, since Zoo
Code, OpenCode, Codex, and Cursor all read it, and native files become thin activators
that point at `prompts/AI_CONTEXT.md`. The contract holds a set of assistants so a project
can serve a mixed team. Project Check verifies that a pointer is loadable, not merely
present.

Provenance becomes mechanical in both directions. Backward, a reference registry binds
every cited work to a resolvable identifier, checked by DOI resolution and title lookup.
Forward, a metrics registry binds every reported number to a logged measurement, written
by instrumented experiment code rather than by prose. Two helper scripts verify each
direction and report; neither edits researcher text and neither refuses to run. The
registries are machine-written, so an assistant can compose an analysis but cannot invent
a number or conjure a paper into either one.

Memory becomes retrievable. Accumulated lessons move from one unbounded file into typed
cards carrying a kind, a stage, a confidence, and mandatory evidence paths. A card without
evidence paths is not a lesson; it is an assertion. A per-stage read plan lets an assistant
load the few cards a stage needs instead of reading every prompt file in the project.

The researcher's decisions become addressable. The five decisions the twelve steps assign
to the researcher get stable gate tokens, so an assistant can be directed to stop at one
and a project can record that it did. Adversarial critique becomes a durable artifact
rather than an instruction, with roles supplied by a domain pack, because structured
critique was the single largest quality contributor in the published ablation.

Domain specificity arrives as data. A domain pack is a YAML file naming vocabulary,
standard baselines, critique roles, and known pitfalls. Adding a domain requires no code.

## User Stories

1. As a researcher who selected Zoo Code, I want the file SMAIRT generates to be a file Zoo Code actually loads, so that project guidance reaches my assistant.
2. As a researcher who selected Cursor, I want the generated rule to carry frontmatter that activates it, so that I do not have to @-mention it every session.
3. As a researcher with an existing project containing `ZOO.md`, I want that file to tell me it is no longer read and where the real file is, so that I am not misled by an artifact SMAIRT created.
4. As a researcher, I want Project Check to report a pointer that cannot be loaded by its assistant, so that silent failure becomes visible.
5. As a researcher, I want to know when a harness supports global rules and why SMAIRT still prefers project rules, so that I can choose deliberately.
6. As a lab lead whose team mixes Claude Code and OpenCode, I want one project to carry both harnesses, so that nobody edits the contract to work.
7. As a researcher switching assistants, I want the previous harness's files reported rather than silently abandoned, so that my project does not accumulate dead guidance.
8. As a researcher, I want an existing project recording a retired assistant to keep loading, so that a tool upgrade never strands my work.
9. As a researcher, I want every citation in my background to carry a resolvable identifier, so that a reference cannot be plausible and absent at once.
10. As a researcher, I want a script that resolves my references and reports which cannot be found, so that verification is not my memory against an assistant's confidence.
11. As a researcher, I want the reference verifier to report and never delete, so that judging a paper's relevance stays mine.
12. As a researcher, I want my experiment code to record its metrics to a registry as it runs, so that the number in my analysis and the number in the log are the same number.
13. As a researcher, I want a script that checks every number in an analysis against the registry, so that an unsupported claim is found before a reader finds it.
14. As a researcher, I want claim verification to report rather than block, so that the tool never refuses my scientific work.
15. As a researcher, I want an assistant unable to write to either registry, so that grounding is structural rather than instructed.
16. As a researcher returning after a month, I want an assistant to retrieve the few lessons relevant to my current stage, so that context is spent on the work.
17. As a researcher, I want every lesson card to cite the evidence it came from, so that a lesson can be re-examined rather than trusted.
18. As a researcher, I want superseded lessons marked rather than deleted, so that a reversal remains visible.
19. As a researcher in computational biology, I want my domain's vocabulary and standard baselines available to an assistant, so that I do not restate them each session.
20. As a researcher in a domain SMAIRT does not ship, I want to add a pack as one YAML file, so that domain support is not a code change.
21. As a researcher, I want the decisions I own to be named, so that I can tell an assistant to stop at one and verify that it did.
22. As a researcher, I want a hypothesis critiqued by named adversarial roles before it is tested, so that a weak assumption surfaces before compute is spent.
23. As a researcher, I want critique recorded as an artifact, so that an objection raised and set aside is not lost.
24. As a researcher, I want each iteration to record whether the project proceeded, refined, or pivoted, so that the shape of the work is legible without reading every analysis.
25. As a researcher, I want SMAIRT Lab installable beside upstream SMAIRT, so that adopting it is reversible.

## Implementation Decisions

- The distribution is renamed `smairt-lab` with command `smairt-lab`, coexisting with upstream `smairt`.
- `harnesses.yaml` ships in `src/smairt_lab/assets/` and declares per assistant: `pointer`, `format`, `reads_agents_md`, `launch`, `legacy_pointers`, `global_rules`.
- `format` is one of `plain-md`, `frontmatter-md`, `frontmatter-mdc`, and selects the rendered body.
- `frontmatter-md` and `frontmatter-mdc` emit `description`, `globs`, and `alwaysApply: true`. Zoo Code and Cursor share this schema, so one renderer serves both.
- `zoo-code` renders `.roo/rules/smairt.md`. `ZOO.md` is declared a legacy pointer.
- `cursor` renders `.cursor/rules/smairt.mdc` with `alwaysApply: true`.
- `claude-code` renders `CLAUDE.md`; `opencode`, `codex`, and `pi` render `AGENTS.md`.
- Activators stay minimal and point at `prompts/AI_CONTEXT.md`, because an always-applied rule costs context on every request.
- A legacy pointer is rewritten to a deprecation note naming the correct path. It is never deleted.
- A researcher-modified legacy pointer is reported and left unchanged.
- `ProjectContract.assistant` becomes `assistants: list[Assistant]`, non-empty, order-preserving, deduplicated.
- `_migrate` promotes a scalar `assistant` to a single-element list, so existing contracts load unchanged.
- No assistant is removed from the enum. `pi` is retained and adapted.
- Generation renders an activator for every selected assistant.
- Deselecting an assistant reports its artifacts and writes nothing. Deactivation never deletes.
- Project Check gains `harness-pointer-not-loadable` when a pointer exists in a format its harness cannot load, and `legacy-harness-pointer` when a legacy path is present. Both carry deterministic repairs.
- The creation summary, `smairt-lab check --verbose`, and `docs/HARNESSES.md` state, per selected harness, the artifact written, whether it loads automatically, and the global-rules position.
- Global rules are documented as optional and non-authoritative. Cursor cannot back User Rules with a file, and merge precedence can let a personal global rule override a project rule, so project rules remain the version-controlled source.
- The `evidence` capability is added, gating `background/references.yaml`, `analysis/CLAIMS.md`, `results/metrics/`, `scripts/verify_references.py`, and `scripts/verify_claims.py`.
- `AssetCondition` gains `evidence`. `OPTIONAL_CAPABILITIES` becomes registry-driven rather than a hard-coded pair, and the `paper`/`hpc` branches in check and repair are generalized.
- A reference entry records `id`, `citation`, `doi`, `arxiv`, `url`, `added`, and `verified`. `verified` is written only by the verifier.
- `verify_references.py` resolves in order: DOI via CrossRef, title via OpenAlex, arXiv identifier, Semantic Scholar. It classifies each entry `verified`, `unresolved`, or `absent`, prints a report, and exits non-zero when a strict-section reference is unresolved.
- The verifier never classifies relevance and never removes an entry, because relevance is a scientific judgment.
- `scripts/shared/metrics.py` supplies `report_metric(name, value, condition=..., seed=...)` and writes `results/metrics/iteration_NN.json` from instrumented code at run time.
- A metric row records `iteration`, `metric`, `value`, `condition`, `seed`, `log`, and `recorded`. The `log` field binds the row to the run that produced it.
- `verify_claims.py` extracts numerics from an analysis, matches each against the registry scoped per condition, and reports unmatched claims. It never edits the analysis.
- Neither verifier is invoked by `smairt-lab check`, and neither blocks any operation. Both report only.
- Memory lives in `memory/` as cards under `patterns/`, `episodes/`, `decisions/`, and `lessons/`.
- Card frontmatter carries `id`, `kind`, `stage`, `confidence`, `evidence_paths`, `retrieval_hints`, `updated_at`, and optional `supersedes`. `evidence_paths` is required and must be non-empty.
- `memory/INDEX.md` holds the per-stage read plan naming which kinds a stage loads first.
- `KNOWN_PATTERNS.md` is retained, reduced to conventions and environment facts, and points at `memory/` for accumulated lessons. Existing content is never rewritten.
- A domain pack is `domains/<id>.yaml` declaring `display_name`, `vocabulary`, `standard_baselines`, `critique_roles_hypothesis`, `critique_roles_analysis`, `known_pitfalls`, and `metric_conventions`.
- The pack is selected by the existing `project.domain` field. An unrecognized domain resolves to `generic`.
- Packs ship for `generic`, `computational-biology`, and `machine-learning`. Adding one is a YAML file and a test fixture.
- Gate tokens `G1` through `G5` name the research question, the hypothesis, the decision criterion, the revise-advance-stop decision, and the contribution record.
- `analysis/CRITIQUE_NN.md` records adversarial critique with roles drawn from the domain pack, plus which objections were answered and which accepted as limitations.
- `ITERATION_LOG.md` gains a `Decision` column recording `Proceed`, `Refine`, or `Pivot`.
- No component selects a hypothesis, scores an idea, ranks a direction, or decides a gate.

## Testing Decisions

- A test asserts every `harnesses.yaml` pointer and format against the vendor-documented convention, so an invented path cannot ship again.
- A test asserts `.cursor/rules/smairt.mdc` and `.roo/rules/smairt.md` parse as frontmatter and set `alwaysApply: true`.
- A test asserts a project generated for every assistant produces an artifact its descriptor marks loadable.
- A test asserts a contract holding a scalar `assistant` migrates to a single-element list.
- A test asserts a contract holding a retired assistant still loads.
- A test asserts a multi-assistant project renders one activator per selected assistant.
- A test asserts an existing `ZOO.md` is rewritten to a deprecation note and a modified one is preserved.
- A test asserts Project Check reports `harness-pointer-not-loadable` for a frontmatter-less `.mdc`.
- A test asserts the reference verifier reports an unresolvable DOI without removing the entry.
- A test asserts the claim verifier reports an unmatched number and leaves the analysis byte-identical.
- A test asserts a claim matching a registry row under a different condition is reported, not silently accepted.
- A test asserts `report_metric` appends without overwriting and records the log path.
- A test asserts neither verifier is reachable from `smairt-lab check`.
- A test asserts a memory card without `evidence_paths` fails validation.
- A test asserts an unrecognized domain resolves to `generic`.
- A test asserts capability registration is registry-driven by adding a fixture capability without touching check or repair.
- Golden projects are extended with a multi-assistant case and an evidence-enabled case.
- The scaffold content suite is extended to forbid an invented harness path and to forbid a verifier that writes to an analysis file.

## Out of Scope

- Hypothesis generation, scoring, ranking, or selection. The published yield is 21 findings from 4,879 ideas at roughly $4,762 each, and roughly 60% of failures were implementation errors rather than weak hypotheses, so the scoring largely measured coding reliability.
- Orchestrating a harness CLI. Scientific work stays with the assistant; SMAIRT Lab does not become an agent runtime. External orchestrators can drive a project because its artifacts are legible.
- Autonomous continuation, detached execution, monitoring cadence, and connector surfaces.
- LLM-based relevance classification or deletion of a citation.
- Enforcement or refusal in `smairt-lab check` on scientific grounds.
- Any dependency on an external memory service. Markdown with mandatory evidence paths is the substrate.
- SMAIRT context in a harness's global rules. Global rules are not version-controlled and can override project rules.
- The MCP server, deferred to a later effort.
- Semantic assessment of researcher work, in keeping with the existing invariant.
- Migration of projects generated by upstream `smairt`. Scaffold version mismatch continues to report and block package-owned mutation.
- Demos, which still teach the retired model and need their own effort.

## Further Notes

- `src/smairt/models.py` defaults `scaffold_version` to `0.3.0` while the package reports `0.4.0`, so a freshly generated project fails its own version check and is blocked from repair and capability changes. Fixed in issue 01.
- `src/smairt/project.py` `phase_directories()` discards its argument and always returns the synthetic tuple. Masked because the blueprint declares all three phases. Fixed in issue 01.
- `adversarial_review1.md` recorded that Zoo Code had no pointer. The remedy invented `ZOO.md` rather than adopting the documented `.roo/` convention, which is why issue 02 exists.
- Zoo Code documents at `docs.zoocode.dev` and reads the `.roo/` tree, `.roorules`, and `AGENTS.md`.
- Cursor ignores a plain `.md` in `.cursor/rules` because it has no frontmatter, and directs plain markdown to `AGENTS.md`.
- Verifier network access is optional. Both scripts run offline, reporting entries as unresolved rather than failing.
