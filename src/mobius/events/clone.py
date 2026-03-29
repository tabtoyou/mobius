"""Event factories for clone-in-the-loop decisions."""

from mobius.events.base import BaseEvent


def clone_decision_made(
    *,
    decision_id: str,
    lineage_id: str | None,
    topic: str,
    selected_option: str,
    selected_option_index: int | None,
    confidence: float,
    rationale: str,
    log_path: str,
    importance: str,
    signals_used: list[str],
) -> BaseEvent:
    """Record an autonomous digital-clone decision."""
    return BaseEvent(
        type="clone.decision.made",
        aggregate_type="clone",
        aggregate_id=decision_id,
        data={
            "lineage_id": lineage_id,
            "topic": topic,
            "selected_option": selected_option,
            "selected_option_index": selected_option_index,
            "confidence": confidence,
            "rationale": rationale,
            "log_path": log_path,
            "importance": importance,
            "signals_used": signals_used,
        },
    )


def clone_feedback_requested(
    *,
    decision_id: str,
    lineage_id: str | None,
    topic: str,
    confidence: float,
    question_for_user: str,
    log_path: str,
    importance: str,
    timeout_fallback_option: str,
    timeout_fallback_option_index: int | None,
    feedback_timeout_seconds: int,
    feedback_deadline_at: str,
) -> BaseEvent:
    """Record a decision point that still requires the human owner."""
    return BaseEvent(
        type="clone.feedback.requested",
        aggregate_type="clone",
        aggregate_id=decision_id,
        data={
            "lineage_id": lineage_id,
            "topic": topic,
            "confidence": confidence,
            "question_for_user": question_for_user,
            "timeout_fallback_option": timeout_fallback_option,
            "timeout_fallback_option_index": timeout_fallback_option_index,
            "feedback_timeout_seconds": feedback_timeout_seconds,
            "feedback_deadline_at": feedback_deadline_at,
            "log_path": log_path,
            "importance": importance,
        },
    )
