"""Three-stage evaluation pipeline for Mobius.

This module provides the evaluation infrastructure for verifying outputs
through three progressive stages:

1. Stage 1 - Mechanical Verification ($0): Lint, build, test, static analysis
2. Stage 2 - Semantic Evaluation (Standard tier): AC compliance, goal alignment
3. Stage 3 - Multi-Model Consensus (Frontier tier): 3-model voting

Classes:
    CheckResult: Result of a single mechanical check
    CheckType: Types of mechanical checks
    MechanicalResult: Aggregated Stage 1 results
    SemanticResult: Stage 2 LLM evaluation results
    Vote: Single model vote in consensus
    ConsensusResult: Aggregated Stage 3 results
    EvaluationResult: Complete pipeline result
    EvaluationContext: Input context for evaluation
    MechanicalVerifier: Stage 1 checker
    MechanicalConfig: Stage 1 configuration
    SemanticEvaluator: Stage 2 evaluator
    SemanticConfig: Stage 2 configuration
    ConsensusEvaluator: Stage 3 consensus builder
    ConsensusConfig: Stage 3 configuration
    ConsensusTrigger: Trigger matrix implementation
    TriggerType: Types of consensus triggers
    TriggerContext: Context for trigger evaluation
    TriggerResult: Result of trigger evaluation
    TriggerConfig: Trigger thresholds
    EvaluationPipeline: Full pipeline orchestrator
    PipelineConfig: Pipeline configuration
"""

from mobius.evaluation.consensus import (
    DEFAULT_CONSENSUS_MODELS,
    ConsensusConfig,
    ConsensusEvaluator,
    DeliberativeConfig,
    DeliberativeConsensus,
    run_consensus_evaluation,
    run_deliberative_evaluation,
)
from mobius.evaluation.languages import (
    LanguagePreset,
    build_mechanical_config,
    detect_language,
)
from mobius.evaluation.mechanical import (
    MechanicalConfig,
    MechanicalVerifier,
    run_mechanical_verification,
)
from mobius.evaluation.models import (
    CheckResult,
    CheckType,
    ConsensusResult,
    DeliberationResult,
    EvaluationContext,
    EvaluationResult,
    FinalVerdict,
    JudgmentResult,
    MechanicalResult,
    SemanticResult,
    Vote,
    VoterRole,
)
from mobius.evaluation.pipeline import (
    EvaluationPipeline,
    PipelineConfig,
    run_evaluation_pipeline,
)
from mobius.evaluation.semantic import (
    DEFAULT_SEMANTIC_MODEL,
    SemanticConfig,
    SemanticEvaluator,
    run_semantic_evaluation,
)
from mobius.evaluation.trigger import (
    ConsensusTrigger,
    TriggerConfig,
    TriggerContext,
    TriggerResult,
    TriggerType,
    check_consensus_trigger,
)

__all__ = [
    # Models
    "CheckResult",
    "CheckType",
    "ConsensusResult",
    "DeliberationResult",
    "EvaluationContext",
    "EvaluationResult",
    "FinalVerdict",
    "JudgmentResult",
    "MechanicalResult",
    "SemanticResult",
    "Vote",
    "VoterRole",
    # Stage 1
    "LanguagePreset",
    "MechanicalConfig",
    "MechanicalVerifier",
    "build_mechanical_config",
    "detect_language",
    "run_mechanical_verification",
    # Stage 2
    "DEFAULT_SEMANTIC_MODEL",
    "SemanticConfig",
    "SemanticEvaluator",
    "run_semantic_evaluation",
    # Stage 3 - Simple Consensus
    "DEFAULT_CONSENSUS_MODELS",
    "ConsensusConfig",
    "ConsensusEvaluator",
    "run_consensus_evaluation",
    # Stage 3 - Deliberative Consensus
    "DeliberativeConfig",
    "DeliberativeConsensus",
    "run_deliberative_evaluation",
    # Trigger
    "ConsensusTrigger",
    "TriggerConfig",
    "TriggerContext",
    "TriggerResult",
    "TriggerType",
    "check_consensus_trigger",
    # Pipeline
    "EvaluationPipeline",
    "PipelineConfig",
    "run_evaluation_pipeline",
]
