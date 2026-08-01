#!/usr/bin/env python3
"""Create the next numbered experiment script in a selected phase."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

PHASES = {
    "synthetic": "01_synthetic",
    "downloaded": "02_downloaded",
    "real": "03_real_data",
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=PHASES)
    parser.add_argument("description", help="Short script description used in its filename.")
    parser.add_argument("--hypothesis", required=True, help="Hypothesis tested by this script.")
    parser.add_argument("--iteration", type=int, default=1)
    arguments = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    experiments = root / "experiments"
    phase_directory = experiments / PHASES[arguments.phase]
    phase_directory.mkdir(parents=True, exist_ok=True)
    numbers = [
        int(match.group(1))
        for script in experiments.glob("*/script_*.py")
        if (match := re.match(r"script_(\d+)", script.name))
    ]
    number = max(numbers, default=0) + 1
    description = re.sub(r"[^a-z0-9]+", "_", arguments.description.lower()).strip("_")
    if not description:
        parser.error("description must contain a letter or number")
    script_name = f"script_{number:02d}_{description}"
    target = phase_directory / f"{script_name}.py"
    target.write_text(_template(script_name, arguments.hypothesis, arguments.iteration))
    print(f"Created {target.relative_to(root)}")


def _template(script_name: str, hypothesis: str, iteration: int) -> str:
    return f'''#!/usr/bin/env python3
"""Experiment: {script_name}

Hypothesis: {hypothesis}
Iteration: {iteration}
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.shared import TeeLogger, setup_logging

SCRIPT_NAME = "{script_name}"


def main() -> None:
    log_path = setup_logging(SCRIPT_NAME, PROJECT_ROOT / "results" / "logs")
    with TeeLogger(log_path):
        print("Hypothesis: {hypothesis}")
        print("TODO: implement the experiment")
        print(f"Log: {{log_path.relative_to(PROJECT_ROOT)}}")


if __name__ == "__main__":
    main()
'''


if __name__ == "__main__":
    main()
