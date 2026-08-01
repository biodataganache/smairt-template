"""Legacy Cookiecutter adapter validation.

Cookiecutter remains supported for existing users. Its generated launcher calls
the installed package, which is the sole owner of canonical scaffold assets.
"""

import re
import sys

slug = "{{ cookiecutter.project_slug }}"
if not re.fullmatch(r"[a-z][a-z0-9_]*", slug):
    print(
        "ERROR: Project slug must start with a lowercase letter and contain only lowercase letters, numbers, and underscores."
    )
    sys.exit(1)
