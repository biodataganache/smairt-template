# Integrating Demos Folder into SMAIRT Template Repository

This guide details how to integrate this cleaned, PII-free collection of demos into your main `smairt-template` repository inside a folder called `demos/` without leaking old git history or carrying over metadata issues.

---

## Prerequisites

Before following these steps:
1. Ensure your local `smairt-template` repository is clean and on its main development branch.
2. Confirm you have push/PR permissions on the `smairt-template` repository (or a personal fork of it).

---

## Integration Procedure

There are two primary ways to do this. **Option A is recommended** as it is extremely simple, 100% foolproof against history leaks, and easily reviewable in a single Pull Request.

### Option A: Clean Working-Tree File Copy (Recommended)

This approach copies only the files, completely dropping the separate git history of this demos repo. This ensures that the destination repository gets clean, flat files, and the history begins fresh inside the template repo.

1. Create a branch inside `smairt-template`:
   ```bash
   cd /path/to/smairt-template
   git checkout -b feature/add-demos
   ```

2. Create a `demos/` directory in `smairt-template`:
   ```bash
   mkdir -p demos
   ```

3. Copy all contents of this cleaned `smairt_template_demos` directory (excluding its `.git/` folder) into the newly created `demos/` folder:
   ```bash
   # From your shell, run:
   rsync -av --exclude='.git' /path/to/smairt_template_demos/ /path/to/smairt-template/demos/
   ```

4. Stage, commit, and push from your `smairt-template` repository:
   ```bash
   cd /path/to/smairt-template
   git add demos/
   git commit -m "docs: Add curated and cleaned SMAIRT demo collection"
   git push origin feature/add-demos
   ```

5. Open a Pull Request from your branch into the main branch of `smairt-template`.

---

### Option B: Merging Demos as a Subtree (Advanced)

If you strictly want to preserve the newly rewritten commit history (which now only contains de-identified commits under a neutral identity) as part of the `smairt-template` history:

1. Add this cleaned demos repo as a git remote from inside `smairt-template`:
   ```bash
   cd /path/to/smairt-template
   git checkout -b feature/add-demos-subtree
   git remote add local-demos /path/to/smairt_template_demos
   git fetch local-demos
   ```

2. Merge the branch as a subtree into a `demos` prefix:
   ```bash
   git subtree add --prefix=demos local-demos main --squash
   ```

3. Remove the local temporary remote and push:
   ```bash
   git remote remove local-demos
   git push origin feature/add-demos-subtree
   ```

*Note: Option A is strongly preferred unless history preservation is explicitly mandated by your group's repository practices.*
