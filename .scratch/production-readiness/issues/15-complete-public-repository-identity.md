# Complete the public repository identity

Type: task
Status: blocked
Blocked by: 04, 06, 07, 14

## Question

Does the repository present itself consistently as the SMAIRT framework rather than the retired cookiecutter template, and can a publication reader cite and contribute to it?

## Work

- Update the GitHub description and topics from “cookiecutter template” to the current framework identity after the new `main` content is ready.
- Verify the root MIT license is detected and represented correctly after merge.
- Add a correct `CITATION.cff` with the repository's approved title, authorship, organization, version/release status, URL, and preferred citation; do not invent publication metadata.
- Make `.github/CONTRIBUTING.md`, issue templates, support statements, security/contact guidance, and README links agree with the current package and documentation hierarchy.
- Decide whether a code of conduct is required by the owning organization and add only an approved one.
- Remove stale repository badges, sibling-repository links, and “Template” branding where it no longer names a historical reference.

## Resolution

Resolve when a first-time reader sees one name and purpose across GitHub metadata, README, package metadata, citation, license, and contribution paths, with no unsupported publication claim.

## Progress

Everything inside the repository is done. Two items need an account with admin on
`PNNL-CompBio/smairt-template`; mine has `push` but not `admin`, confirmed via the API.

### Done

- **`CITATION.cff` added.** A publication-facing repo a reviewer cannot cite is missing the
  point. Only approved facts are recorded — organization authorship, MIT, the repository URL, the
  real version — with no invented DOI, journal, or author list. A test asserts its version matches
  the package, because that literal is unavoidable there and so is exactly what drifts silently.
- **"Research Template" corrected to "Research Toolkit" in the shipped scaffold.**
  `prompts/AI_CONTEXT.md` was priming every assistant with the retired identity, in a file
  regenerated into every project. Goldens updated through the generator.
- **Broken demo links repaired.** `demos/README.md` pointed two badges and two table rows at
  `../smairt-template/` and `../smairt-agentic/`, sibling directories that do not exist in any
  checkout.
- **Seven of eight `DEMO.md` files told readers to copy a file that is not there.**
  `cp background/01_initial_question.md ...` reads plausibly, but the reference question lives
  inside the completed project, not beside `DEMO.md`. A reader hit
  `No such file or directory` on the first command. A test now asserts every documented `cp`
  source exists.

### Blocked on admin access

1. **Repository description** still reads "The Scientific Method using AI Research Template for
   cookiecutter." Suggested: *"SMAIRT: Scientific Method with AI Research Toolkit — create
   research workspaces that keep a traceable record from hypothesis to result."*
2. **Topics** are empty. Suggested: `reproducible-research`, `scientific-workflow`,
   `research-provenance`, `ai-assisted-research`, `python-cli`.

GitHub license detection resolves itself on merge: `LICENSE` exists on this branch and not on
`main`, which is why the repository currently reports no license.

### Deliberately not done

No code of conduct was added. Adding an unapproved one to a PNNL repository would be presumptuous
about an organizational policy I cannot verify.
