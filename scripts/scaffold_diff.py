#!/usr/bin/env python3
"""Show review-sensitive differences between two scaffold blueprints."""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from smairt.scaffold import diff_blueprints


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("previous", type=Path)
    parser.add_argument("current", type=Path)
    arguments = parser.parse_args()
    differences = diff_blueprints(
        yaml.safe_load(arguments.previous.read_text()),
        yaml.safe_load(arguments.current.read_text()),
    )
    for category, entries in differences.items():
        print(f"{category.replace('_', ' ').title()}:")
        if entries:
            for entry in entries:
                print(f"  - {entry}")
        else:
            print("  (none)")


if __name__ == "__main__":
    main()
