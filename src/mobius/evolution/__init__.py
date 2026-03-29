"""Mobius evolution module - evolutionary loop for ontology evolution.

Transforms the linear pipeline (Interview → Seed → Execute → Evaluate → DONE)
into a closed evolutionary loop where ontology evolves across generations:

    Gen 1: Interview → Seed(O₁) → Execute → Evaluate
                                                  │
    Gen 2: Wonder → Reflect → Seed(O₂) → Execute → Evaluate
                                                        │
    Gen 3: Wonder → Reflect → Seed(O₃) → Execute → Evaluate
                                                        │
                                              [convergence check]
"""

from mobius.evolution.convergence import ConvergenceCriteria, ConvergenceSignal
from mobius.evolution.loop import (
    EvolutionaryLoop,
    EvolutionaryLoopConfig,
    EvolutionaryResult,
    GenerationResult,
    StepAction,
    StepResult,
)
from mobius.evolution.projector import LineageProjector
from mobius.evolution.reflect import OntologyMutation, ReflectEngine, ReflectOutput
from mobius.evolution.wonder import WonderEngine, WonderOutput

__all__ = [
    # Loop
    "EvolutionaryLoop",
    "EvolutionaryLoopConfig",
    "EvolutionaryResult",
    "GenerationResult",
    "StepAction",
    "StepResult",
    # Engines
    "WonderEngine",
    "ReflectEngine",
    # Outputs
    "WonderOutput",
    "ReflectOutput",
    "OntologyMutation",
    # Convergence
    "ConvergenceCriteria",
    "ConvergenceSignal",
    # Projection
    "LineageProjector",
]
