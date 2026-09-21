"""One-click preset circuits (Phase 13 of the plan)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Preset:
    key: str
    label: str
    initial: str          # key into quantum.qubit.INITIAL_STATES
    gates: List[str]      # gate symbols
    concept: str


PRESETS: List[Preset] = [
    Preset(
        key="superposition",
        label="Create superposition",
        initial="0",
        gates=["H"],
        concept="H maps |0⟩ to |+⟩ — a 50/50 superposition of |0⟩ and |1⟩.",
    ),
    Preset(
        key="phase_flip",
        label="Phase flip",
        initial="0",
        gates=["H", "Z"],
        concept="Z changes the phase of the superposition (|+⟩ → |−⟩) without changing the 50/50 probabilities.",
    ),
    Preset(
        key="hadamard_inverse",
        label="Hadamard inverse",
        initial="0",
        gates=["H", "H"],
        concept="H² = I, so two Hadamards return the qubit to |0⟩.",
    ),
    Preset(
        key="bit_flip",
        label="Bit flip",
        initial="0",
        gates=["X"],
        concept="X maps |0⟩ to |1⟩ — the quantum NOT gate.",
    ),
    Preset(
        key="hzx",
        label="H → Z → X walkthrough",
        initial="0",
        gates=["H", "Z", "X"],
        concept="The plan's worked example: |0⟩ → |+⟩ → |−⟩ → −|−⟩. The final X only adds a global phase.",
    ),
]
