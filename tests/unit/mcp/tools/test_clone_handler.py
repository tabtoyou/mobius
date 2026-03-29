"""Tests for the Mobius clone decision MCP tool."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

from mobius.core.types import Result
from mobius.mcp.tools.clone_handler import CloneDecisionHandler
from mobius.mcp.tools.definitions import get_mobius_tools
from mobius.orchestrator.adapter import TaskResult
from mobius.persistence.event_store import EventStore


class TestCloneDecisionHandler:
    """Validate clone decision routing behavior."""

    async def test_handle_selects_option_and_persists_log(self, tmp_path: Path) -> None:
        store = EventStore("sqlite+aiosqlite:///:memory:")
        runtime = MagicMock()
        runtime.execute_task_to_result = AsyncMock(
            return_value=Result.ok(
                TaskResult(
                    success=True,
                    final_message="""
                        {
                          "action": "choose_option",
                          "selected_option_index": 1,
                          "confidence": 0.82,
                          "rationale": "Prior projects favored explicit adapter layers.",
                          "decision_log_summary": "Use an adapter abstraction for the new integration.",
                          "signals_used": ["existing adapter pattern", "avoid direct coupling"],
                          "question_for_user": null,
                          "timeout_fallback_option_index": null
                        }
                    """,
                    messages=(),
                )
            )
        )
        handler = CloneDecisionHandler(
            event_store=store,
            agent_runtime=runtime,
            runtime_backend="codex",
            llm_backend="codex",
        )

        result = await handler.handle(
            {
                "topic": "transport integration shape",
                "context": "We need to choose how the new notifier plugs into the loop.",
                "options": ["inline integration", "adapter abstraction"],
                "importance": "high",
                "project_dir": str(tmp_path),
                "notify_channel": "log",
            }
        )

        assert result.is_ok
        assert result.value.meta["selected_option"] == "adapter abstraction"
        assert result.value.meta["requires_human_feedback"] is False
        assert result.value.meta["timeout_fallback_option"] is None
        assert result.value.meta["feedback_deadline_at"] is None
        assert result.value.meta["continue_without_human_feedback"] is False

        log_path = Path(result.value.meta["decision_log_path"])
        assert log_path.exists()
        assert "adapter abstraction" in log_path.read_text(encoding="utf-8")

        events = await store.replay("clone", result.value.meta["decision_id"])
        assert len(events) == 1
        assert events[0].type == "clone.decision.made"

    async def test_handle_escalates_when_confidence_is_too_low(self, tmp_path: Path) -> None:
        store = EventStore("sqlite+aiosqlite:///:memory:")
        runtime = MagicMock()
        runtime.execute_task_to_result = AsyncMock(
            return_value=Result.ok(
                TaskResult(
                    success=True,
                    final_message="""
                        {
                          "action": "choose_option",
                          "selected_option_index": 0,
                          "confidence": 0.41,
                          "rationale": "There is some precedent, but not enough for a critical choice.",
                          "decision_log_summary": "Clone could not safely choose the persistence strategy.",
                          "signals_used": ["weak prior preference"],
                          "question_for_user": null,
                          "timeout_fallback_option_index": null
                        }
                    """,
                    messages=(),
                )
            )
        )
        handler = CloneDecisionHandler(
            event_store=store,
            agent_runtime=runtime,
            runtime_backend="codex",
            llm_backend="codex",
        )

        result = await handler.handle(
            {
                "topic": "persistence strategy",
                "context": "This determines how prior-project memory is stored and reused.",
                "options": ["sqlite event stream", "markdown memory file"],
                "importance": "critical",
                "project_dir": str(tmp_path),
                "notify_channel": "log",
            }
        )

        assert result.is_ok
        assert result.value.meta["selected_option"] is None
        assert result.value.meta["requires_human_feedback"] is True
        assert "question_for_user" in result.value.meta
        assert result.value.meta["timeout_fallback_option"] == "sqlite event stream"
        assert result.value.meta["feedback_timeout_seconds"] == 300
        assert result.value.meta["feedback_deadline_at"] is not None
        assert result.value.meta["continue_without_human_feedback"] is True
        assert "do not block Ralph loop" in result.value.text_content

        events = await store.replay("clone", result.value.meta["decision_id"])
        assert len(events) == 1
        assert events[0].type == "clone.feedback.requested"
        assert events[0].data["timeout_fallback_option"] == "sqlite event stream"
        assert events[0].data["feedback_deadline_at"] == result.value.meta["feedback_deadline_at"]

    async def test_handle_degrades_open_when_subagent_fails(self, tmp_path: Path) -> None:
        runtime = MagicMock()
        runtime.execute_task_to_result = AsyncMock(return_value=Result.err(RuntimeError("boom")))
        handler = CloneDecisionHandler(
            agent_runtime=runtime,
            runtime_backend="codex",
            llm_backend="codex",
        )

        result = await handler.handle(
            {
                "topic": "schema storage shape",
                "context": "Need a clone decision but the subagent crashed.",
                "options": ["jsonl", "sqlite"],
                "project_dir": str(tmp_path),
            }
        )

        assert result.is_ok
        assert result.value.meta["requires_human_feedback"] is True
        assert result.value.meta["degraded"] is True
        assert result.value.meta["timeout_fallback_option"] == "jsonl"
        assert result.value.meta["feedback_deadline_at"] is not None
        assert "human feedback required" in result.value.text_content.lower()

    async def test_handle_degrades_open_when_options_is_invalid_string(
        self, tmp_path: Path
    ) -> None:
        handler = CloneDecisionHandler(runtime_backend="codex", llm_backend="codex")

        result = await handler.handle(
            {
                "topic": "bad input",
                "context": "Caller sent malformed options.",
                "options": "jsonl",
                "project_dir": str(tmp_path),
            }
        )

        assert result.is_ok
        assert result.value.meta["requires_human_feedback"] is True
        assert result.value.meta["degraded"] is True

    def test_definitions_include_clone_tool(self) -> None:
        tool_names = [handler.definition.name for handler in get_mobius_tools()]
        assert "mobius_clone_decide" in tool_names
