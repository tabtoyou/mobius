"""MCP tool handler for Mobius digital clone decisions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from mobius.clone import CloneDecisionEngine, CloneDecisionRequest
from mobius.core.errors import MobiusError, ValidationError
from mobius.core.types import Result
from mobius.mcp.errors import MCPServerError
from mobius.mcp.types import (
    ContentType,
    MCPContentItem,
    MCPToolDefinition,
    MCPToolParameter,
    MCPToolResult,
    ToolInputType,
)
from mobius.persistence.event_store import EventStore
from mobius.providers.base import LLMAdapter


@dataclass
class CloneDecisionHandler:
    """Resolve ambiguous choices using a profile-backed digital clone."""

    event_store: EventStore | None = field(default=None, repr=False)
    llm_adapter: LLMAdapter | None = field(default=None, repr=False)
    agent_runtime: Any | None = field(default=None, repr=False)
    runtime_backend: str | None = None
    llm_backend: str | None = None
    clone_engine: CloneDecisionEngine | None = field(default=None, repr=False)

    @property
    def definition(self) -> MCPToolDefinition:
        """Return the clone decision tool definition."""
        return MCPToolDefinition(
            name="mobius_clone_decide",
            description=(
                "Resolve an ambiguous implementation choice using the user's digital clone. "
                "The clone chooses a prior-consistent option or explicitly requests human feedback."
            ),
            parameters=(
                MCPToolParameter(
                    name="topic",
                    type=ToolInputType.STRING,
                    description="Short label for the decision that needs to be made.",
                    required=True,
                ),
                MCPToolParameter(
                    name="context",
                    type=ToolInputType.STRING,
                    description="Current execution context and why the decision matters.",
                    required=True,
                ),
                MCPToolParameter(
                    name="options",
                    type=ToolInputType.ARRAY,
                    description="Candidate options to choose between.",
                    required=True,
                    items={"type": "string"},
                ),
                MCPToolParameter(
                    name="lineage_id",
                    type=ToolInputType.STRING,
                    description="Optional Ralph lineage id for traceability.",
                    required=False,
                ),
                MCPToolParameter(
                    name="importance",
                    type=ToolInputType.STRING,
                    description="Decision criticality. Higher importance makes escalation more likely.",
                    required=False,
                    default="medium",
                    enum=("low", "medium", "high", "critical"),
                ),
                MCPToolParameter(
                    name="project_dir",
                    type=ToolInputType.STRING,
                    description="Project directory used to locate clone profile and logs.",
                    required=False,
                ),
                MCPToolParameter(
                    name="profile_path",
                    type=ToolInputType.STRING,
                    description="Optional explicit path to the clone memory/profile document.",
                    required=False,
                ),
                MCPToolParameter(
                    name="decision_log_path",
                    type=ToolInputType.STRING,
                    description="Optional explicit path for the JSONL decision log.",
                    required=False,
                ),
                MCPToolParameter(
                    name="notify_channel",
                    type=ToolInputType.STRING,
                    description="Notification mode for the decision record.",
                    required=False,
                    default="auto",
                    enum=("auto", "log", "slack", "imessage", "none"),
                ),
            ),
        )

    async def handle(
        self,
        arguments: dict[str, Any],
    ) -> Result[MCPToolResult, MCPServerError]:
        """Handle a clone decision request."""
        fallback_request = CloneDecisionRequest(
            topic=str(arguments.get("topic", "unspecified clone decision")),
            context=str(arguments.get("context", "Clone request could not be parsed cleanly.")),
            options=("request user feedback", "continue conservatively"),
            lineage_id=(
                str(arguments["lineage_id"]) if arguments.get("lineage_id") is not None else None
            ),
            importance=str(arguments.get("importance", "medium")),
            project_dir=(
                str(arguments["project_dir"]) if arguments.get("project_dir") is not None else None
            ),
            profile_path=(
                str(arguments["profile_path"])
                if arguments.get("profile_path") is not None
                else None
            ),
            decision_log_path=(
                str(arguments["decision_log_path"])
                if arguments.get("decision_log_path") is not None
                else None
            ),
            notify_channel=str(arguments.get("notify_channel", "auto")),
        )
        try:
            raw_options = arguments.get("options", ())
            if isinstance(raw_options, str):
                raise ValueError("options must be an array, not a string")
            request = CloneDecisionRequest(
                topic=str(arguments.get("topic", "")),
                context=str(arguments.get("context", "")),
                options=tuple(
                    str(option)
                    for option in raw_options
                    if isinstance(option, str | int | float | bool)
                ),
                lineage_id=(
                    str(arguments["lineage_id"])
                    if arguments.get("lineage_id") is not None
                    else None
                ),
                importance=str(arguments.get("importance", "medium")),
                project_dir=(
                    str(arguments["project_dir"])
                    if arguments.get("project_dir") is not None
                    else None
                ),
                profile_path=(
                    str(arguments["profile_path"])
                    if arguments.get("profile_path") is not None
                    else None
                ),
                decision_log_path=(
                    str(arguments["decision_log_path"])
                    if arguments.get("decision_log_path") is not None
                    else None
                ),
                notify_channel=str(arguments.get("notify_channel", "auto")),
            )
        except Exception as exc:
            degraded = CloneDecisionEngine(
                event_store=self.event_store,
                llm_adapter=self.llm_adapter,
                agent_runtime=self.agent_runtime,
                runtime_backend=self.runtime_backend,
                llm_backend=self.llm_backend,
            )._fallback_result(
                fallback_request,
                decision_id="clone-degraded-parse",
                reason=f"Failed to parse clone decision arguments: {exc}",
            )
            return self._build_success_response(degraded)

        engine = self.clone_engine or CloneDecisionEngine(
            llm_adapter=self.llm_adapter,
            agent_runtime=self.agent_runtime,
            runtime_backend=self.runtime_backend,
            llm_backend=self.llm_backend,
            event_store=self.event_store,
        )

        try:
            result = await engine.decide(request)
        except (ValidationError, MobiusError) as exc:
            degraded = engine._fallback_result(
                request,
                decision_id="clone-degraded-handler",
                reason=str(exc),
            )
            result = Result.ok(degraded)

        if result.is_err:
            degraded = engine._fallback_result(
                request,
                decision_id="clone-degraded-handler",
                reason=str(result.error),
            )
            result = Result.ok(degraded)

        return self._build_success_response(result.value)

    def _build_success_response(
        self,
        decision: Any,
    ) -> Result[MCPToolResult, MCPServerError]:
        selected_line = (
            decision.selected_option
            if decision.selected_option is not None
            else "human feedback required"
        )
        question_block = (
            f"\nQuestion for user: {decision.question_for_user}"
            if decision.question_for_user
            else ""
        )
        timeout_block = (
            "\nTimeout fallback: "
            f"{decision.timeout_fallback_option} after {decision.feedback_timeout_seconds}s"
            if decision.timeout_fallback_option
            else ""
        )
        deadline_block = (
            f"\nFeedback deadline (UTC): {decision.feedback_deadline_at}"
            if decision.feedback_deadline_at
            else ""
        )
        policy_block = (
            "\nExecution policy: ask the user once if reachable, but do not block Ralph loop. "
            f"If no reply arrives by the deadline, continue with {decision.timeout_fallback_option}."
            if decision.timeout_fallback_option
            else ""
        )
        notification_block = ", ".join(decision.notification_status)
        text = (
            "Mobius Clone Decision\n"
            f"Decision ID: {decision.decision_id}\n"
            f"Action: {decision.action}\n"
            f"Selected: {selected_line}\n"
            f"Confidence: {decision.confidence:.2f}\n"
            f"Summary: {decision.decision_log_summary}\n"
            f"Rationale: {decision.rationale}\n"
            f"Signals: {', '.join(decision.signals_used) or 'none'}\n"
            f"Decision Log: {decision.log_path}\n"
            f"Notifications: {notification_block}"
            f"{question_block}{timeout_block}{deadline_block}{policy_block}"
        )
        return Result.ok(
            MCPToolResult(
                content=(MCPContentItem(type=ContentType.TEXT, text=text),),
                meta={
                    "decision_id": decision.decision_id,
                    "action": decision.action,
                    "selected_option": decision.selected_option,
                    "selected_option_index": decision.selected_option_index,
                    "confidence": decision.confidence,
                    "requires_human_feedback": decision.requires_human_feedback,
                    "question_for_user": decision.question_for_user,
                    "timeout_fallback_option": decision.timeout_fallback_option,
                    "timeout_fallback_option_index": decision.timeout_fallback_option_index,
                    "feedback_timeout_seconds": decision.feedback_timeout_seconds,
                    "feedback_deadline_at": decision.feedback_deadline_at,
                    "continue_without_human_feedback": bool(decision.timeout_fallback_option),
                    "decision_log_path": decision.log_path,
                    "profile_path": decision.profile_path,
                    "notify_channel": decision.notify_channel,
                    "notification_status": list(decision.notification_status),
                    "degraded": decision.confidence == 0.0,
                },
            )
        )
