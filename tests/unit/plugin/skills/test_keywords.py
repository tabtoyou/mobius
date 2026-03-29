"""Unit tests for exact magic keyword routing."""

from pathlib import Path

import pytest

from mobius.plugin.skills.keywords import MatchType, is_magic_command, route_to_skill
from mobius.plugin.skills.registry import SkillRegistry


async def _discover_registry(tmp_path: Path) -> SkillRegistry:
    skill_dir = tmp_path / "skills"
    skill_dir.mkdir()

    for skill_name in ("run", "interview", "welcome"):
        skill_path = skill_dir / skill_name
        skill_path.mkdir()
        (skill_path / "SKILL.md").write_text(
            f"""---
name: {skill_name}
description: {skill_name} skill
---

# {skill_name}
""",
            encoding="utf-8",
        )

    registry = SkillRegistry(skill_dir=skill_dir)
    await registry.discover_all()
    return registry


class TestExactMagicCommandEligibility:
    """Test deterministic intercept eligibility checks."""

    @pytest.mark.parametrize(
        ("user_input", "expected"),
        [
            ("mob run", True),
            ("mob run seed.yaml", True),
            ("mob:run seed.yaml", True),
            ("/mobius:run seed.yaml", True),
            ("mobius:run seed.yaml", True),
            ('mob interview "Build an API"', True),
            ("mob", True),
            ("/mobius", True),
            ("mobius", True),
            ("please mob run", False),
            ("note /mobius:run", False),
            ("I used mob run yesterday", False),
            ("mob r", False),
        ],
    )
    def test_is_magic_command_requires_exact_prefix(
        self,
        user_input: str,
        expected: bool,
    ) -> None:
        """Only exact start-of-input command forms are eligible."""
        assert is_magic_command(user_input) is expected


class TestExactMagicKeywordRouting:
    """Test exact prefix routing against discovered skills."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("user_input", "expected_skill"),
        [
            ("mob run seed.yaml", "run"),
            ("mob:run seed.yaml", "run"),
            ("/mobius:run seed.yaml", "run"),
            ("mobius:run seed.yaml", "run"),
            ("mob interview Build an API", "interview"),
            ("mob", "welcome"),
            ("/mobius", "welcome"),
        ],
    )
    async def test_route_to_skill_accepts_all_exact_prefix_variants(
        self,
        tmp_path: Path,
        user_input: str,
        expected_skill: str,
    ) -> None:
        """Exact prefixes should resolve directly to the matching skill."""
        registry = await _discover_registry(tmp_path)

        try:
            skill_name, match_type = route_to_skill(user_input, registry)
        finally:
            registry.stop_watcher()

        assert skill_name == expected_skill
        assert match_type == MatchType.EXACT_PREFIX

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "user_input",
        [
            "please mob run seed.yaml",
            "note /mobius:run seed.yaml",
            "mob r",
            "/mobius:r",
        ],
    )
    async def test_route_to_skill_rejects_partial_or_embedded_prefixes(
        self,
        tmp_path: Path,
        user_input: str,
    ) -> None:
        """Partial and embedded commands should fall through."""
        registry = await _discover_registry(tmp_path)

        try:
            skill_name, match_type = route_to_skill(user_input, registry)
        finally:
            registry.stop_watcher()

        assert skill_name is None
        assert match_type == MatchType.FALLBACK
