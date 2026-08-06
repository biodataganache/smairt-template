#!/usr/bin/env python3
"""Create an unnumbered utility script in `scripts/utilities/`.

A utility is code that supports the research without being an attempt at the research
question: a data downloader, a figure regenerator, a one-off inspection. It is not an
iteration, so it takes no iteration number and appears in no record.

That separation is deliberate. Iteration numbers are a timeline of attempts, and a
utility taking a number would leave a gap in `analysis/ITERATION_LOG.md` that looks like
a lost attempt. Use `new_iteration.py` for anything that tests something.

Nothing is overwritten. If the file is already there, this refuses rather than replacing
it.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.shared.iterations import project_root, slugify, write_new_script  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("description", help="Short description used in the filename.")
    parser.add_argument(
        "--purpose",
        required=True,
        help="What this utility is for, recorded in its docstring.",
    )
    arguments = parser.parse_args()

    root = project_root()
    name = slugify(arguments.description)
    if not name:
        parser.error("description must contain a letter or number")

    target = root / "scripts" / "utilities" / f"{name}.py"
    try:
        write_new_script(target, _template(name, arguments.purpose))
    except FileExistsError as error:
        parser.error(str(error))

    print(f"Created {target.relative_to(root)}")
    print("This is a utility, not an iteration: no number was taken and no row was added.")
    print("If it tests something, create an iteration instead: python3 scripts/new_iteration.py")


def _template(name: str, purpose: str) -> str:
    return f'''#!/usr/bin/env python3
"""Utility: {name}

Purpose: {purpose}

This is not an iteration. It supports the work rather than testing a hypothesis, so it
carries no iteration number and no row in analysis/ITERATION_LOG.md.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.shared import TeeLogger, setup_logging, write_provenance

SCRIPT_NAME = "{name}"


def main() -> None:
    log_path = setup_logging(SCRIPT_NAME, PROJECT_ROOT / "results" / "logs")
    with TeeLogger(log_path):
        write_provenance(project_root=PROJECT_ROOT, config={{}})
        print("Purpose: {purpose}")
        print("TODO: implement the utility")
        print(f"Log: {{log_path.relative_to(PROJECT_ROOT)}}")


if __name__ == "__main__":
    main()
'''


if __name__ == "__main__":
    main()
