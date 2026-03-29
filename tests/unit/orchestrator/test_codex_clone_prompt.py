"""Tests for clone-in-the-loop prompt guidance."""

from mobius.orchestrator.codex_cli_runtime import CodexCliRuntime


class TestCodexClonePrompt:
    """Prompt composition should advertise the clone decision tool."""

    def test_compose_prompt_adds_clone_protocol_when_tool_is_available(self) -> None:
        runtime = CodexCliRuntime(cli_path="codex", cwd="/tmp/project")

        prompt = runtime._compose_prompt(
            "Implement the task.",
            "Follow the seed.",
            ["Read", "mobius_clone_decide"],
        )

        assert "Clone-In-The-Loop Protocol" in prompt
        assert "mobius_clone_decide" in prompt
        assert "If no human reply arrives within 5 minutes" in prompt
        assert "do not block Ralph loop waiting for a reply" in prompt
