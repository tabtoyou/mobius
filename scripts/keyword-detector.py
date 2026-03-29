#!/usr/bin/env python3
"""Magic Keyword Detector for Mobius.

Detects trigger keywords in user prompts and suggests
the appropriate Mobius skill to invoke.

IMPORTANT: If MCP is not configured (mob setup not run),
ALL mob commands (except setup/help) redirect to setup first.

Hook: UserPromptSubmit
Input: User prompt text via stdin (piped by Claude Code)
Output: Modified prompt with skill suggestion appended
"""

import json
from pathlib import Path
import re
import sys

# Skills that work without MCP setup (bypass the setup gate)
# qa has a built-in fallback that adopts the qa-judge agent directly
SETUP_BYPASS_SKILLS = [
    "/mobius:setup",
    "/mobius:help",
    "/mobius:qa",
]

# Keyword → skill mapping
# "mob <cmd>" prefix always works; natural language keywords also supported
KEYWORD_MAP = [
    # mob prefix shortcuts (checked first for priority)
    {"patterns": ["mob interview", "mob socratic"], "skill": "/mobius:interview"},
    {"patterns": ["mob seed", "mob crystallize"], "skill": "/mobius:seed"},
    {"patterns": ["mob run", "mob execute"], "skill": "/mobius:run"},
    {"patterns": ["mob eval", "mob evaluate"], "skill": "/mobius:evaluate"},
    {"patterns": ["mob evolve"], "skill": "/mobius:evolve"},
    {"patterns": ["mob stuck", "mob unstuck", "mob lateral"], "skill": "/mobius:unstuck"},
    {"patterns": ["mob status", "mob drift"], "skill": "/mobius:status"},
    {"patterns": ["mob ralph"], "skill": "/mobius:ralph"},
    {"patterns": ["mob tutorial"], "skill": "/mobius:tutorial"},
    {"patterns": ["mob welcome"], "skill": "/mobius:welcome"},
    {"patterns": ["mob setup"], "skill": "/mobius:setup"},
    {"patterns": ["mob help"], "skill": "/mobius:help"},
    {"patterns": ["mob pm", "mob prd"], "skill": "/mobius:pm"},
    {"patterns": ["mob qa", "qa check", "quality check"], "skill": "/mobius:qa"},
    {"patterns": ["mob cancel", "mob abort"], "skill": "/mobius:cancel"},
    {"patterns": ["mob update", "mob upgrade"], "skill": "/mobius:update"},
    {"patterns": ["mob brownfield"], "skill": "/mobius:brownfield"},
    # Natural language triggers
    # PM triggers must precede generic interview to avoid "pm interview" being shadowed
    {
        "patterns": [
            "write prd",
            "pm interview",
            "product requirements",
            "create prd",
        ],
        "skill": "/mobius:pm",
    },
    {
        "patterns": [
            "interview me",
            "clarify requirements",
            "clarify my requirements",
            "socratic interview",
            "socratic questioning",
        ],
        "skill": "/mobius:interview",
    },
    {
        "patterns": ["crystallize", "generate seed", "create seed", "freeze requirements"],
        "skill": "/mobius:seed",
    },
    {
        "patterns": ["mobius run", "execute seed", "run seed", "run workflow"],
        "skill": "/mobius:run",
    },
    {
        "patterns": ["evaluate this", "3-stage check", "three-stage", "verify execution"],
        "skill": "/mobius:evaluate",
    },
    {
        "patterns": ["evolve", "evolutionary loop", "iterate until converged"],
        "skill": "/mobius:evolve",
    },
    {
        "patterns": [
            "think sideways",
            "i'm stuck",
            "im stuck",
            "i am stuck",
            "break through",
            "lateral thinking",
        ],
        "skill": "/mobius:unstuck",
    },
    {
        "patterns": [
            "am i drifting",
            "drift check",
            "session status",
            "check drift",
            "goal deviation",
        ],
        "skill": "/mobius:status",
    },
    {
        "patterns": ["ralph", "don't stop", "must complete", "until it works", "keep going"],
        "skill": "/mobius:ralph",
    },
    {"patterns": ["mobius setup", "setup mobius"], "skill": "/mobius:setup"},
    {"patterns": ["mobius help"], "skill": "/mobius:help"},
    {
        "patterns": ["update mobius", "upgrade mobius"],
        "skill": "/mobius:update",
    },
    {
        "patterns": [
            "cancel execution",
            "stop job",
            "kill stuck",
            "abort execution",
        ],
        "skill": "/mobius:cancel",
    },
    {
        "patterns": [
            "brownfield defaults",
            "brownfield scan",
        ],
        "skill": "/mobius:brownfield",
    },
]


def is_mcp_configured() -> bool:
    """Check if MCP server is registered in ~/.claude/mcp.json."""
    try:
        mcp_path = Path.home() / ".claude" / "mcp.json"
        if not mcp_path.exists():
            return False
        return "mobius" in mcp_path.read_text()
    except Exception:
        return False


def is_first_time() -> bool:
    """Check if this is the user's first interaction (welcome not yet completed)."""
    try:
        prefs_path = Path.home() / ".mobius" / "prefs.json"
        if not prefs_path.exists():
            return True
        prefs = json.loads(prefs_path.read_text())
        return not prefs.get("welcomeCompleted", False)
    except Exception:
        return True


def _word_boundary_match(pattern: str, text: str) -> bool:
    """Match pattern using word boundaries to avoid false positives."""
    return bool(re.search(r"(?:^|\b)" + re.escape(pattern) + r"(?:\b|$)", text))


def detect_keywords(text: str) -> dict:
    """Detect keywords in user prompt text."""
    lower = text.lower().strip()

    for entry in KEYWORD_MAP:
        for pattern in entry["patterns"]:
            if _word_boundary_match(pattern, lower):
                return {
                    "detected": True,
                    "keyword": pattern,
                    "suggested_skill": entry["skill"],
                }

    # Bare "mob" (with no subcommand) → welcome (first-touch experience)
    if lower in ("mob", "mob?"):
        return {
            "detected": True,
            "keyword": "mob",
            "suggested_skill": "/mobius:welcome",
        }

    return {"detected": False, "keyword": None, "suggested_skill": None}


def main() -> None:
    # Read user prompt from stdin
    try:
        user_input = sys.stdin.read().strip()
    except Exception:
        user_input = ""

    result = detect_keywords(user_input)

    # First-time user: append welcome suggestion to their first message
    if not result["detected"] and is_first_time():
        skill_name = "welcome"
        print(f"""{user_input}

<skill-suggestion>
🎯 MATCHED SKILLS (use AskUserQuestion to let user choose):
- /mobius:{skill_name} - First time using Mobius! Starting welcome experience.
IMPORTANT: Auto-triggering welcome experience now. Use AskUserQuestion to confirm or skip.
</skill-suggestion>
""")
        return

    if result["detected"]:
        skill = result["suggested_skill"]
        keyword = result["keyword"]

        # Gate check: if MCP not configured and skill requires it, redirect to setup
        if skill not in SETUP_BYPASS_SKILLS and not is_mcp_configured():
            print(f"""{user_input}

<skill-suggestion>
🎯 REQUIRED SKILL:
- /mobius:setup - Mobius setup required. Run "mob setup" first to register the MCP server.
</skill-suggestion>
""")
        else:
            skill_name = skill.replace("/mobius:", "")
            print(f"""{user_input}

<skill-suggestion>
🎯 MATCHED SKILLS:
- /mobius:{skill_name} - Detected "{keyword}"
</skill-suggestion>
""")
    else:
        # Pass through unchanged when no keyword detected
        print(user_input)


if __name__ == "__main__":
    main()
