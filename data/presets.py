"""One-click example circuits (Phase 13 of the plan, extended to several qubits)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

OperationSpec = Tuple[str, Tuple[int, ...]]


@dataclass(frozen=True)
class Preset:
    key: str
    label: str
    num_qubits: int
    initial: Tuple[str, ...]              # INITIAL_STATES key per qubit
    operations: Tuple[OperationSpec, ...]
    concept: str


PRESETS: List[Preset] = [
    Preset("superposition", "Create superposition", 1, ("0",), (("H", (0,)),),
           "H maps |0⟩ to |+⟩ — a 50/50 superposition of |0⟩ and |1⟩."),
    Preset("phase_flip", "Phase flip", 1, ("0",), (("H", (0,)), ("Z", (0,))),
           "Z changes the phase of the superposition (|+⟩ → |−⟩) without changing the 50/50 probabilities."),
    Preset("hadamard_inverse", "Hadamard inverse", 1, ("0",), (("H", (0,)), ("H", (0,))),
           "H² = I, so two Hadamards return the qubit to |0⟩."),
    Preset("bit_flip", "Bit flip", 1, ("0",), (("X", (0,)),),
           "X maps |0⟩ to |1⟩ — the quantum NOT gate."),
    Preset("hzx", "H → Z → X walkthrough", 1, ("0",), (("H", (0,)), ("Z", (0,)), ("X", (0,))),
           "The plan's worked example: |0⟩ → |+⟩ → |−⟩ → −|−⟩. The final X only adds a global phase."),
    Preset("quarter_turns", "S·S = Z (quarter turns)", 1, ("0",), (("H", (0,)), ("S", (0,)), ("S", (0,))),
           "Each S rotates the equator by 90°: |+⟩ → |+i⟩ → |−⟩. Two quarter turns make the half turn Z."),
    Preset("bell", "Bell state |Φ⁺⟩ (2 qubits)", 2, ("0", "0"), (("H", (0,)), ("CNOT", (0, 1))),
           "H then CNOT turns |00⟩ into (|00⟩ + |11⟩)/√2. The qubits become entangled: each Bloch arrow shrinks to nothing."),
    Preset("independent", "Two independent qubits", 2, ("0", "0"), (("H", (0,)), ("X", (1,))),
           "Gates on different qubits act independently: the state stays a product |+⟩ ⊗ |1⟩ and both arrows keep full length."),
    Preset("swap_demo", "SWAP (2 qubits)", 2, ("0", "1"), (("SWAP", (0, 1)),),
           "SWAP exchanges the two qubits: |01⟩ becomes |10⟩."),
    Preset("ghz", "GHZ state (3 qubits)", 3, ("0", "0", "0"), (("H", (0,)), ("CNOT", (0, 1)), ("CNOT", (1, 2))),
           "Entanglement spreads: (|000⟩ + |111⟩)/√2. Measuring any one qubit fixes the other two."),
]

PRESETS_BY_KEY = {p.key: p for p in PRESETS}
