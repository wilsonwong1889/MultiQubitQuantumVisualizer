"""Plain-language teaching text for each gate (Phase 12 of the plan)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class GateDescription:
    title: str
    summary: str                 # one or two sentences shown under the maths
    basis_actions: List[str]     # what it does to common basis states (LaTeX)
    bloch: str                   # geometric meaning on the Bloch sphere
    tip: str                     # a short "notice that ..." remark


GATE_DESCRIPTIONS: Dict[str, GateDescription] = {
    "H": GateDescription(
        title="Hadamard gate",
        summary=(
            "The Hadamard gate turns a definite state into an equal superposition. "
            "Each output amplitude is a sum of both input amplitudes, scaled by 1/√2, "
            "so from |0⟩ both outcomes become equally likely."
        ),
        basis_actions=[
            r"H|0\rangle = \tfrac{1}{\sqrt{2}}(|0\rangle + |1\rangle) = |+\rangle",
            r"H|1\rangle = \tfrac{1}{\sqrt{2}}(|0\rangle - |1\rangle) = |-\rangle",
            r"H|+\rangle = |0\rangle",
            r"H|-\rangle = |1\rangle",
        ],
        bloch="180° rotation about the diagonal (x + z)/√2 axis, which swaps the Z axis with the X axis.",
        tip="Applying H twice returns the original state because H·H = I.",
    ),
    "X": GateDescription(
        title="Pauli-X gate (bit flip)",
        summary=(
            "The X gate is the quantum NOT: it swaps the amplitudes of |0⟩ and |1⟩. "
            "Whatever probability |0⟩ had is now the probability of |1⟩, and vice versa."
        ),
        basis_actions=[
            r"X|0\rangle = |1\rangle",
            r"X|1\rangle = |0\rangle",
            r"X|+\rangle = |+\rangle",
            r"X|-\rangle = -|-\rangle",
        ],
        bloch="180° rotation about the X axis: the north pole |0⟩ swaps with the south pole |1⟩.",
        tip="|+⟩ and |−⟩ lie on the X axis, so X leaves them in place (|−⟩ only picks up a global sign).",
    ),
    "Y": GateDescription(
        title="Pauli-Y gate",
        summary=(
            "The Y gate is a bit flip and a phase flip at once (Y = iXZ). It swaps the "
            "amplitudes and multiplies them by ±i, so the imaginary parts matter here."
        ),
        basis_actions=[
            r"Y|0\rangle = i|1\rangle",
            r"Y|1\rangle = -i|0\rangle",
            r"Y|+\rangle = -i|-\rangle",
            r"Y|-\rangle = i|+\rangle",
        ],
        bloch="180° rotation about the Y axis: |0⟩ ↔ |1⟩ and |+⟩ ↔ |−⟩, while |+i⟩ and |−i⟩ stay fixed.",
        tip="The factors of i are invisible in the probabilities but show up as the direction of rotation.",
    ),
    "Z": GateDescription(
        title="Pauli-Z gate (phase flip)",
        summary=(
            "The Z gate leaves α alone and multiplies β by −1. The measurement "
            "probabilities do not change at all, because |−β|² = |β|² — only the relative phase changes."
        ),
        basis_actions=[
            r"Z|0\rangle = |0\rangle",
            r"Z|1\rangle = -|1\rangle",
            r"Z|+\rangle = |-\rangle",
            r"Z|-\rangle = |+\rangle",
        ],
        bloch="180° rotation about the Z axis: |+⟩ ↔ |−⟩, while the poles |0⟩ and |1⟩ do not move.",
        tip="Z on |+⟩ is the clearest demonstration that a phase change is real even though the 50/50 probabilities stay the same.",
    ),
}
