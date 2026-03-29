"""Digital clone decision engine for clone-in-the-loop workflows."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
import json
import os
from pathlib import Path
import subprocess
from typing import Any
import urllib.error
import urllib.request
from uuid import uuid4

from mobius.config import get_clarification_model
from mobius.core.errors import ConfigError, MobiusError, ValidationError
from mobius.core.types import Result
from mobius.evaluation.json_utils import extract_json_payload
from mobius.events.clone import clone_decision_made, clone_feedback_requested
from mobius.execution.subagent import (
    create_subagent_completed_event,
    create_subagent_failed_event,
    create_subagent_started_event,
)
from mobius.orchestrator.adapter import AgentRuntime
from mobius.orchestrator.runtime_factory import create_agent_runtime
from mobius.persistence.event_store import EventStore
from mobius.providers import create_llm_adapter
from mobius.providers.base import CompletionConfig, LLMAdapter, Message, MessageRole

_DEFAULT_PROFILE_LOCATIONS = (
    ".mobius/clone_profile.md",
    ".mobius/memory.md",
)
_DEFAULT_LOG_LOCATION = ".mobius/clone-decisions.jsonl"
_IMPORTANCE_VALUES = ("low", "medium", "high", "critical")
_NOTIFY_CHANNEL_VALUES = ("auto", "log", "slack", "imessage", "none")
_MIN_CONFIDENCE_BY_IMPORTANCE = {
    "low": 0.35,
    "medium": 0.5,
    "high": 0.7,
    "critical": 0.8,
}
_DEFAULT_FEEDBACK_TIMEOUT_SECONDS = 300
_DECISION_SCHEMA: dict[str, Any] = {
    "name": "clone_decision",
    "schema": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["choose_option", "request_user_feedback"],
            },
            "selected_option_index": {
                "type": ["integer", "null"],
                "minimum": 0,
            },
            "confidence": {
                "type": "number",
                "minimum": 0.0,
                "maximum": 1.0,
            },
            "rationale": {"type": "string"},
            "decision_log_summary": {"type": "string"},
            "signals_used": {
                "type": "array",
                "items": {"type": "string"},
            },
            "question_for_user": {
                "type": ["string", "null"],
            },
            "timeout_fallback_option_index": {
                "type": ["integer", "null"],
                "minimum": 0,
            },
        },
        "required": [
            "action",
            "selected_option_index",
            "confidence",
            "rationale",
            "decision_log_summary",
            "signals_used",
            "question_for_user",
            "timeout_fallback_option_index",
        ],
        "additionalProperties": False,
    },
}


@dataclass(frozen=True, slots=True)
class CloneDecisionRequest:
    """Input for a digital clone decision."""

    topic: str
    context: str
    options: tuple[str, ...]
    lineage_id: str | None = None
    importance: str = "medium"
    project_dir: str | None = None
    profile_path: str | None = None
    decision_log_path: str | None = None
    notify_channel: str = "auto"


@dataclass(frozen=True, slots=True)
class CloneDecisionResult:
    """Structured result from the digital clone."""

    decision_id: str
    action: str
    selected_option: str | None
    selected_option_index: int | None
    confidence: float
    rationale: str
    decision_log_summary: str
    signals_used: tuple[str, ...]
    question_for_user: str | None
    timeout_fallback_option: str | None
    timeout_fallback_option_index: int | None
    feedback_timeout_seconds: int
    feedback_deadline_at: str | None
    profile_path: str | None
    log_path: str
    notify_channel: str
    notification_status: tuple[str, ...]
    project_dir: str | None

    @property
    def requires_human_feedback(self) -> bool:
        """Return True when the clone refuses to decide autonomously."""
        return self.action == "request_user_feedback"


class CloneDecisionEngine:
    """Use a profile-backed LLM to decide ambiguous implementation choices."""

    def __init__(
        self,
        *,
        llm_adapter: LLMAdapter | None = None,
        agent_runtime: AgentRuntime | None = None,
        runtime_backend: str | None = None,
        llm_backend: str | None = None,
        event_store: EventStore | None = None,
    ) -> None:
        self._llm_adapter = llm_adapter
        self._agent_runtime = agent_runtime
        self._runtime_backend = runtime_backend
        self._llm_backend = llm_backend
        self._event_store = event_store

    async def decide(
        self,
        request: CloneDecisionRequest,
    ) -> Result[CloneDecisionResult, MobiusError]:
        """Resolve an ambiguous choice using the configured digital clone."""
        normalized = self._normalize_request(request)
        profile_path = self._resolve_profile_path(normalized)
        profile_content = self._load_profile(profile_path)
        decision_id = f"clone-{datetime.now(UTC).strftime('%Y%m%d%H%M%S%f')}-{uuid4().hex[:8]}"

        try:
            raw_response = await self._run_decision_agent(
                normalized,
                profile_path=profile_path,
                profile_content=profile_content,
                decision_id=decision_id,
            )
            parsed = self._parse_response(raw_response, normalized, decision_id=decision_id)
            result = (
                parsed.value
                if parsed.is_ok
                else self._fallback_result(
                    normalized,
                    decision_id=decision_id,
                    reason=str(parsed.error),
                )
            )
        except Exception as exc:
            result = self._fallback_result(
                normalized,
                decision_id=decision_id,
                reason=f"clone sub-agent failed: {exc}",
            )

        log_path = self._write_log(result, normalized)
        notification_status = self._notify(result, normalized, log_path)
        final_result = CloneDecisionResult(
            decision_id=result.decision_id,
            action=result.action,
            selected_option=result.selected_option,
            selected_option_index=result.selected_option_index,
            confidence=result.confidence,
            rationale=result.rationale,
            decision_log_summary=result.decision_log_summary,
            signals_used=result.signals_used,
            question_for_user=result.question_for_user,
            timeout_fallback_option=result.timeout_fallback_option,
            timeout_fallback_option_index=result.timeout_fallback_option_index,
            feedback_timeout_seconds=result.feedback_timeout_seconds,
            feedback_deadline_at=result.feedback_deadline_at,
            profile_path=str(profile_path) if profile_path else None,
            log_path=str(log_path),
            notify_channel=normalized.notify_channel,
            notification_status=notification_status,
            project_dir=normalized.project_dir,
        )

        await self._record_event(final_result, normalized)
        return Result.ok(final_result)

    async def _run_llm_fallback(
        self,
        request: CloneDecisionRequest,
        *,
        profile_path: Path | None,
        profile_content: str,
    ) -> str:
        adapter = self._llm_adapter or create_llm_adapter(
            backend=self._llm_backend,
            use_case="interview",
            cwd=request.project_dir,
            max_turns=1,
        )
        llm_result = await adapter.complete(
            messages=[
                Message(
                    role=MessageRole.SYSTEM, content=self._build_system_prompt(profile_content)
                ),
                Message(
                    role=MessageRole.USER, content=self._build_user_prompt(request, profile_path)
                ),
            ],
            config=CompletionConfig(
                model=get_clarification_model(self._llm_backend),
                temperature=0.2,
                max_tokens=1400,
                response_format={
                    "type": "json_schema",
                    "json_schema": _DECISION_SCHEMA,
                },
            ),
        )
        if llm_result.is_err:
            raise llm_result.error
        return llm_result.value.content

    def _normalize_request(self, request: CloneDecisionRequest) -> CloneDecisionRequest:
        topic = request.topic.strip()
        context = request.context.strip()
        options = tuple(option.strip() for option in request.options if option.strip())
        importance = request.importance.strip().lower()
        notify_channel = request.notify_channel.strip().lower()

        if not topic:
            raise ValidationError("topic is required", field="topic")
        if not context:
            raise ValidationError("context is required", field="context")
        if len(options) < 2:
            raise ValidationError(
                "at least two options are required for clone decision routing",
                field="options",
                value=list(request.options),
            )
        if importance not in _IMPORTANCE_VALUES:
            raise ValidationError(
                f"importance must be one of {', '.join(_IMPORTANCE_VALUES)}",
                field="importance",
                value=request.importance,
            )
        if notify_channel not in _NOTIFY_CHANNEL_VALUES:
            raise ValidationError(
                f"notify_channel must be one of {', '.join(_NOTIFY_CHANNEL_VALUES)}",
                field="notify_channel",
                value=request.notify_channel,
            )

        project_dir = request.project_dir
        if project_dir:
            project_dir = str(Path(project_dir).expanduser().resolve())

        return CloneDecisionRequest(
            topic=topic,
            context=context,
            options=options,
            lineage_id=request.lineage_id.strip() if request.lineage_id else None,
            importance=importance,
            project_dir=project_dir,
            profile_path=request.profile_path,
            decision_log_path=request.decision_log_path,
            notify_channel=notify_channel,
        )

    def _resolve_profile_path(self, request: CloneDecisionRequest) -> Path | None:
        candidates: list[Path] = []
        base = Path(request.project_dir) if request.project_dir else Path.cwd()

        if request.profile_path:
            path = Path(request.profile_path).expanduser()
            if not path.is_absolute():
                path = (base / path).resolve()
            candidates.append(path)

        for env_name in ("MOBIUS_CLONE_PROFILE_PATH",):
            env_value = os.environ.get(env_name)
            if env_value:
                candidates.append(Path(env_value).expanduser())

        candidates.extend(base / rel for rel in _DEFAULT_PROFILE_LOCATIONS)

        for candidate in candidates:
            if candidate.exists() and candidate.is_file():
                return candidate.resolve()
        return None

    def _load_profile(self, profile_path: Path | None) -> str:
        if profile_path is None:
            return (
                "No persisted digital-clone profile was found. Favor conservative choices, "
                "respect existing project patterns, and escalate when confidence is low."
            )
        try:
            return profile_path.read_text(encoding="utf-8").strip()
        except OSError as exc:
            raise ConfigError(
                f"Failed to read clone profile: {exc}",
                config_file=str(profile_path),
            ) from exc

    def _build_system_prompt(self, profile_content: str) -> str:
        return f"""You are a digital clone acting as clone-in-the-loop for an autonomous coding agent.

Your job is to make the same kinds of implementation choices the human owner would make,
using their prior decisions, architectural taste, and constraints. Do not invent authority.
If the profile or current context does not justify a safe choice, ask for human feedback.

Profile and memory:
{profile_content}

Decision policy:
- Prefer consistency with prior philosophy over local convenience.
- Prefer reversible decisions when confidence is limited.
- If the choice is important and confidence is low, request human feedback.
- Respond as JSON only."""

    def _build_user_prompt(
        self,
        request: CloneDecisionRequest,
        profile_path: Path | None,
    ) -> str:
        options = "\n".join(f"{index}. {option}" for index, option in enumerate(request.options))
        return f"""Decide one ambiguous implementation choice for the autonomous loop.

Topic: {request.topic}
Importance: {request.importance}
Lineage ID: {request.lineage_id or "unknown"}
Project Dir: {request.project_dir or "unknown"}
Profile Path: {profile_path or "none"}

Context:
{request.context}

Options:
{options}

Return JSON with:
- action: choose_option or request_user_feedback
- selected_option_index: null when escalating
- confidence: 0.0 to 1.0
- rationale: concise reasoning tied to the profile/context
- decision_log_summary: short summary for logs/notifications
- signals_used: brief bullets naming the memories, patterns, or constraints used
- question_for_user: required only when escalating, otherwise null
- timeout_fallback_option_index: required when escalating; the option to use if the human does not answer within 300 seconds"""

    def _build_subagent_system_prompt(self, profile_content: str) -> str:
        return f"""You are Mobius Clone, a digital human sub-agent used inside Ralph loop.

You are not a normal code-writing agent. Your sole task is to make or escalate an ambiguous decision
using the owner's historical preferences, nearby repositories, and current code context.

You may inspect local repositories, browse files, and use search/fetch tools when helpful.
Do not modify files. Read, inspect, compare, and decide.

Owner memory:
{profile_content}

Output requirements:
- Return JSON only.
- If you cannot justify a safe decision, return action=request_user_feedback.
- If you escalate, still provide timeout_fallback_option_index for the best fallback after 300 seconds.
- Never hang waiting for the human. Make the best bounded attempt, then escalate."""

    def _build_subagent_prompt(
        self,
        request: CloneDecisionRequest,
        profile_path: Path | None,
    ) -> str:
        options = "\n".join(f"{index}. {option}" for index, option in enumerate(request.options))
        project_dir = request.project_dir or str(Path.cwd())
        sibling_hint = str(Path(project_dir).resolve().parent)
        return f"""Make one clone-in-the-loop decision.

Decision topic: {request.topic}
Importance: {request.importance}
Lineage ID: {request.lineage_id or "unknown"}
Project directory: {project_dir}
Nearby repositories root to inspect if useful: {sibling_hint}
Profile path: {profile_path or "none"}

Current context:
{request.context}

Candidate options:
{options}

Process:
1. Inspect the current project and nearby repos only as needed.
2. Infer which option best matches the owner's prior engineering choices.
3. If the evidence is weak for this importance level, escalate instead of guessing.

Return strict JSON with these fields:
{{
  "action": "choose_option" | "request_user_feedback",
  "selected_option_index": integer | null,
  "confidence": number,
  "rationale": string,
  "decision_log_summary": string,
  "signals_used": [string],
  "question_for_user": string | null,
  "timeout_fallback_option_index": integer | null
}}"""

    async def _run_decision_agent(
        self,
        request: CloneDecisionRequest,
        *,
        profile_path: Path | None,
        profile_content: str,
        decision_id: str,
    ) -> str:
        if (
            self._agent_runtime is None
            and self._runtime_backend is None
            and self._llm_adapter is not None
        ):
            return await self._run_llm_fallback(
                request,
                profile_path=profile_path,
                profile_content=profile_content,
            )

        runtime = self._agent_runtime or create_agent_runtime(
            backend=self._runtime_backend,
            llm_backend=self._llm_backend,
            cwd=request.project_dir,
        )
        await self._record_subagent_event(
            create_subagent_started_event(
                subagent_id=decision_id,
                parent_execution_id=request.lineage_id or decision_id,
                child_ac=request.topic,
                depth=0,
            )
        )

        task_result = await runtime.execute_task_to_result(
            prompt=self._build_subagent_prompt(request, profile_path),
            system_prompt=self._build_subagent_system_prompt(profile_content),
            tools=["Read", "Glob", "Grep", "Bash", "WebFetch", "WebSearch"],
        )
        if task_result.is_err:
            await self._record_subagent_event(
                create_subagent_failed_event(
                    subagent_id=decision_id,
                    parent_execution_id=request.lineage_id or decision_id,
                    error_message=str(task_result.error),
                    is_retriable=False,
                )
            )
            raise task_result.error

        await self._record_subagent_event(
            create_subagent_completed_event(
                subagent_id=decision_id,
                parent_execution_id=request.lineage_id or decision_id,
                success=True,
                child_count=0,
            )
        )
        return task_result.value.final_message

    def _parse_response(
        self,
        response_text: str,
        request: CloneDecisionRequest,
        *,
        decision_id: str,
    ) -> Result[CloneDecisionResult, MobiusError]:
        payload = extract_json_payload(response_text)
        if payload is None:
            return Result.err(
                ValidationError(
                    "Could not find JSON in clone decision response",
                    field="response_text",
                )
            )

        try:
            data = json.loads(payload)
        except json.JSONDecodeError as exc:
            return Result.err(
                ValidationError(
                    f"Invalid JSON in clone decision response: {exc}",
                    field="response_text",
                )
            )

        action = str(data.get("action", "")).strip()
        if action not in {"choose_option", "request_user_feedback"}:
            return Result.err(
                ValidationError(
                    "clone action must be choose_option or request_user_feedback",
                    field="action",
                    value=action,
                )
            )

        raw_index = data.get("selected_option_index")
        selected_index = raw_index if isinstance(raw_index, int) else None
        confidence = data.get("confidence")
        if not isinstance(confidence, (int, float)):
            return Result.err(
                ValidationError(
                    "clone confidence must be numeric",
                    field="confidence",
                    value=confidence,
                )
            )
        confidence_value = min(1.0, max(0.0, float(confidence)))

        rationale = str(data.get("rationale", "")).strip()
        summary = str(data.get("decision_log_summary", "")).strip()
        signals = data.get("signals_used", [])
        question_for_user = data.get("question_for_user")
        raw_timeout_fallback_index = data.get("timeout_fallback_option_index")
        timeout_fallback_index = (
            raw_timeout_fallback_index if isinstance(raw_timeout_fallback_index, int) else None
        )

        if not rationale:
            return Result.err(ValidationError("clone rationale is required", field="rationale"))
        if not summary:
            return Result.err(
                ValidationError(
                    "clone decision_log_summary is required",
                    field="decision_log_summary",
                )
            )
        if not isinstance(signals, list):
            signals = []
        signal_values = tuple(str(item).strip() for item in signals if str(item).strip())

        selected_option: str | None = None
        timeout_fallback_option: str | None = None
        enforced_action = action
        if action == "choose_option":
            if selected_index is None or not 0 <= selected_index < len(request.options):
                return Result.err(
                    ValidationError(
                        "selected_option_index must reference one of the provided options",
                        field="selected_option_index",
                        value=raw_index,
                    )
                )
            selected_option = request.options[selected_index]
            minimum_confidence = _MIN_CONFIDENCE_BY_IMPORTANCE[request.importance]
            if confidence_value < minimum_confidence:
                enforced_action = "request_user_feedback"
                timeout_fallback_index = selected_index
                timeout_fallback_option = selected_option
                selected_option = None
                selected_index = None
                if not question_for_user:
                    question_for_user = (
                        f"I found several viable directions for '{request.topic}', but the "
                        "profile/history was not strong enough to choose safely."
                    )
        else:
            selected_index = None
            question_for_user = str(question_for_user).strip() if question_for_user else None
            if not question_for_user:
                return Result.err(
                    ValidationError(
                        "question_for_user is required when requesting human feedback",
                        field="question_for_user",
                    )
                )

        if enforced_action == "request_user_feedback":
            if timeout_fallback_index is None or not 0 <= timeout_fallback_index < len(
                request.options
            ):
                timeout_fallback_index = self._default_timeout_fallback_index(request)
            timeout_fallback_option = request.options[timeout_fallback_index]
        else:
            timeout_fallback_index = None
            timeout_fallback_option = None

        return Result.ok(
            CloneDecisionResult(
                decision_id=decision_id,
                action=enforced_action,
                selected_option=selected_option,
                selected_option_index=selected_index,
                confidence=confidence_value,
                rationale=rationale,
                decision_log_summary=summary,
                signals_used=signal_values,
                question_for_user=(
                    str(question_for_user).strip() if question_for_user is not None else None
                ),
                timeout_fallback_option=timeout_fallback_option,
                timeout_fallback_option_index=timeout_fallback_index,
                feedback_timeout_seconds=_DEFAULT_FEEDBACK_TIMEOUT_SECONDS,
                feedback_deadline_at=self._build_feedback_deadline_at(enforced_action),
                profile_path=None,
                log_path="",
                notify_channel=request.notify_channel,
                notification_status=(),
                project_dir=request.project_dir,
            )
        )

    def _fallback_result(
        self,
        request: CloneDecisionRequest,
        *,
        decision_id: str,
        reason: str,
    ) -> CloneDecisionResult:
        summary = f"Clone degraded for '{request.topic}'; escalating without blocking Ralph loop."
        question = (
            f"Clone could not confidently decide '{request.topic}'. "
            "Review the alternatives when convenient."
        )
        timeout_fallback_index = self._default_timeout_fallback_index(request)
        return CloneDecisionResult(
            decision_id=decision_id,
            action="request_user_feedback",
            selected_option=None,
            selected_option_index=None,
            confidence=0.0,
            rationale=reason,
            decision_log_summary=summary,
            signals_used=("degraded_clone_fallback",),
            question_for_user=question,
            timeout_fallback_option=request.options[timeout_fallback_index],
            timeout_fallback_option_index=timeout_fallback_index,
            feedback_timeout_seconds=_DEFAULT_FEEDBACK_TIMEOUT_SECONDS,
            feedback_deadline_at=self._build_feedback_deadline_at("request_user_feedback"),
            profile_path=None,
            log_path="",
            notify_channel=request.notify_channel,
            notification_status=(),
            project_dir=request.project_dir,
        )

    def _default_timeout_fallback_index(self, request: CloneDecisionRequest) -> int:
        if not request.options:
            return 0
        return 0

    def _build_feedback_deadline_at(self, action: str) -> str | None:
        if action != "request_user_feedback":
            return None
        deadline = datetime.now(UTC) + timedelta(seconds=_DEFAULT_FEEDBACK_TIMEOUT_SECONDS)
        return deadline.isoformat()

    def _resolve_log_path(self, request: CloneDecisionRequest) -> Path:
        if request.decision_log_path:
            path = Path(request.decision_log_path).expanduser()
            if not path.is_absolute():
                base = Path(request.project_dir) if request.project_dir else Path.cwd()
                return (base / path).resolve()
            return path
        base = Path(request.project_dir) if request.project_dir else Path.cwd()
        return base / _DEFAULT_LOG_LOCATION

    def _write_log(self, result: CloneDecisionResult, request: CloneDecisionRequest) -> Path:
        log_path = self._resolve_log_path(request).resolve()
        log_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "timestamp": datetime.now(UTC).isoformat(),
            "decision_id": result.decision_id,
            "lineage_id": request.lineage_id,
            "topic": request.topic,
            "importance": request.importance,
            "action": result.action,
            "selected_option_index": result.selected_option_index,
            "selected_option": result.selected_option,
            "confidence": result.confidence,
            "decision_log_summary": result.decision_log_summary,
            "rationale": result.rationale,
            "signals_used": list(result.signals_used),
            "question_for_user": result.question_for_user,
            "timeout_fallback_option_index": result.timeout_fallback_option_index,
            "timeout_fallback_option": result.timeout_fallback_option,
            "feedback_timeout_seconds": result.feedback_timeout_seconds,
            "feedback_deadline_at": result.feedback_deadline_at,
            "project_dir": request.project_dir,
        }
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=True) + "\n")
        return log_path

    async def _record_event(
        self,
        result: CloneDecisionResult,
        request: CloneDecisionRequest,
    ) -> None:
        if self._event_store is None:
            return

        await self._event_store.initialize()
        if result.requires_human_feedback:
            event = clone_feedback_requested(
                decision_id=result.decision_id,
                lineage_id=request.lineage_id,
                topic=request.topic,
                confidence=result.confidence,
                question_for_user=result.question_for_user or "",
                log_path=result.log_path,
                importance=request.importance,
                timeout_fallback_option=result.timeout_fallback_option or "",
                timeout_fallback_option_index=result.timeout_fallback_option_index,
                feedback_timeout_seconds=result.feedback_timeout_seconds,
                feedback_deadline_at=result.feedback_deadline_at or "",
            )
        else:
            event = clone_decision_made(
                decision_id=result.decision_id,
                lineage_id=request.lineage_id,
                topic=request.topic,
                selected_option=result.selected_option or "",
                selected_option_index=result.selected_option_index,
                confidence=result.confidence,
                rationale=result.rationale,
                log_path=result.log_path,
                importance=request.importance,
                signals_used=list(result.signals_used),
            )
        await self._event_store.append(event)

    async def _record_subagent_event(self, event: Any) -> None:
        if self._event_store is None:
            return
        await self._event_store.initialize()
        await self._event_store.append(event)

    def _notify(
        self,
        result: CloneDecisionResult,
        request: CloneDecisionRequest,
        log_path: Path,
    ) -> tuple[str, ...]:
        channel = request.notify_channel
        if channel in {"none", "log"}:
            return ("log_only",)

        message = self._build_notification_message(result, request, log_path)
        statuses = ["log_only"]
        if channel in {"auto", "slack"}:
            statuses.append(self._notify_slack(message))
            if channel == "slack":
                return tuple(statuses)
        if channel in {"auto", "imessage"}:
            statuses.append(self._notify_imessage(message))
        return tuple(statuses)

    def _build_notification_message(
        self,
        result: CloneDecisionResult,
        request: CloneDecisionRequest,
        log_path: Path,
    ) -> str:
        lines = [
            f"[Mobius clone] {request.topic}",
            f"importance={request.importance}",
            f"confidence={result.confidence:.2f}",
            f"action={result.action}",
            f"log={log_path}",
        ]
        if result.selected_option:
            lines.append(f"selected={result.selected_option}")
        if result.question_for_user:
            lines.append(f"question={result.question_for_user}")
        if result.timeout_fallback_option:
            lines.append(
                f"timeout_fallback={result.timeout_fallback_option}@{result.feedback_timeout_seconds}s"
            )
        if result.feedback_deadline_at:
            lines.append(f"deadline={result.feedback_deadline_at}")
        lines.append(f"summary={result.decision_log_summary}")
        return " | ".join(lines)

    def _notify_slack(self, message: str) -> str:
        webhook_url = os.environ.get("MOBIUS_CLONE_SLACK_WEBHOOK_URL")
        if not webhook_url:
            return "slack_not_configured"

        request = urllib.request.Request(
            webhook_url,
            data=json.dumps({"text": message}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=5):
                return "slack_sent"
        except (urllib.error.URLError, TimeoutError, ValueError):
            return "slack_failed"

    def _notify_imessage(self, message: str) -> str:
        recipient = os.environ.get("MOBIUS_CLONE_IMESSAGE_RECIPIENT")
        if not recipient:
            return "imessage_not_configured"

        script = [
            'tell application "Messages"',
            "set targetService to 1st service whose service type = iMessage",
            f"set targetBuddy to buddy {self._apple_script_quote(recipient)} of targetService",
            f"send {self._apple_script_quote(message)} to targetBuddy",
            "end tell",
        ]
        try:
            subprocess.run(
                ["osascript", *sum((["-e", line] for line in script), start=[])],
                check=True,
                capture_output=True,
                text=True,
            )
        except (FileNotFoundError, subprocess.SubprocessError):
            return "imessage_failed"
        return "imessage_sent"

    def _apple_script_quote(self, value: str) -> str:
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
