"""Measurement in the computational basis (Born rule + collapse)."""
from __future__ import annotations

import random
from typing import Dict, Optional, Tuple

from .complex_number import ZERO
from .state import QuantumState, basis_state


def sample(state: QuantumState, shots: int, seed: Optional[int] = None) -> Dict[str, int]:
    """Repeat the whole experiment `shots` times and count the outcomes."""
    if shots < 1:
        raise ValueError("shots must be positive")
    rng = random.Random(seed)
    labels = state.basis_labels()
    draws = rng.choices(labels, weights=state.probabilities(), k=shots)
    counts = {label: 0 for label in labels}
    for label in draws:
        counts[label] += 1
    return counts


def collapse(state: QuantumState, label: str) -> QuantumState:
    """The post-measurement state after observing `label`."""
    if state.probability_of(label) <= 0.0:
        raise ValueError(f"Outcome {label!r} has zero probability")
    return basis_state(label)


def measure_once(state: QuantumState, seed: Optional[int] = None) -> Tuple[str, QuantumState]:
    """One shot: returns (outcome label, collapsed state)."""
    outcome = _draw(state, seed)
    return outcome, collapse(state, outcome)


def _draw(state: QuantumState, seed: Optional[int]) -> str:
    rng = random.Random(seed)
    return rng.choices(state.basis_labels(), weights=state.probabilities(), k=1)[0]


def measure_qubit(state: QuantumState, qubit: int, seed: Optional[int] = None) -> Tuple[int, QuantumState]:
    """Measure a single qubit and leave the others in their (possibly updated) state.

    Amplitudes inconsistent with the outcome are removed and the rest are
    renormalised -- for an entangled pair this is how measuring one qubit
    fixes the other.
    """
    p1 = sum(a.magnitude_squared() for i, a in enumerate(state.amplitudes) if state.bit(i, qubit) == 1)
    rng = random.Random(seed)
    outcome = 1 if rng.random() < p1 else 0
    keep = p1 if outcome == 1 else 1.0 - p1
    scale = 1.0 / (keep ** 0.5)
    new_amps = tuple(
        a.scale(scale) if state.bit(i, qubit) == outcome else ZERO
        for i, a in enumerate(state.amplitudes)
    )
    return outcome, QuantumState(new_amps)
