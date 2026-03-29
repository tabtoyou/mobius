#!/usr/bin/env python3
"""Drift Monitor for Mobius.

Monitors file changes (Write/Edit tool calls) and checks
if there's an active Mobius session that may be drifting.

Hook: PostToolUse (Write|Edit)
Output: Advisory message if active session detected

This is a lightweight check - actual drift measurement
requires calling /mobius:status with the MCP server.
"""

from pathlib import Path
import time


def check_active_session() -> dict:
    """Check for active Mobius interview sessions."""
    mobius_dir = Path.home() / ".mobius" / "data"

    if not mobius_dir.exists():
        return {"active": False}

    try:
        files = [
            f
            for f in mobius_dir.iterdir()
            if f.suffix == ".json"
            and not f.name.endswith(".lock")
            and f.name.startswith("interview_")
        ]

        if not files:
            return {"active": False}

        # Find the most recent session
        newest = max(files, key=lambda f: f.stat().st_mtime)
        newest_time = newest.stat().st_mtime

        # Only consider sessions modified in the last hour
        one_hour_ago = time.time() - 3600
        if newest_time < one_hour_ago:
            return {"active": False}

        return {"active": True, "session_file": newest.name}
    except Exception:
        return {"active": False}


def main() -> None:
    session = check_active_session()

    if session["active"]:
        print(
            f"Mobius session active ({session['session_file']}). "
            f"Use /mobius:status to check drift."
        )
    else:
        print("Success")


if __name__ == "__main__":
    main()
