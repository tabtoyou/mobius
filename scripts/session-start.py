#!/usr/bin/env python3
"""Session Start Hook for Mobius.

Checks for available updates on session start (cached, max once per 24h).

Hook: SessionStart
"""

import importlib.util
from pathlib import Path
import sys


def main() -> None:
    try:
        script_path = str(Path(__file__).parent / "version-check.py")
        spec = importlib.util.spec_from_file_location("version_check", script_path)
        checker = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(checker)

        result = checker.check_update()
        if result.get("update_available") and result.get("message"):
            # Print update notice — Claude Code shows this as hook output
            print(result["message"])
            return
    except Exception as e:
        print(f"mobius: update check failed: {e}", file=sys.stderr)

    print("Success")


if __name__ == "__main__":
    main()
