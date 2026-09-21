"""The gate library.

Single-qubit gates are 2x2 matrices; two-qubit gates are 4x4. Every
single-qubit gate here is a rotation of the Bloch sphere about some axis, so it
records that axis and angle for the animation. To add a gate, define it below
and add it to GATES -- the UI, circuit model and tests pick it up from there.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from .complex_number import Complex, I, ONE, ZERO
from .matrix import Matrix, Matrix2x2

INV_SQRT2 = 1.0 / math.sqrt(2.0)


@dataclass(frozen=True)
class Gate:
    name: str
    symbol: str
    matrix: Matrix
    description: str
    arity: int = 1                                   # how many qubits it acts on
    axis: Optional[Tuple[float, float, float]] = None  # Bloch rotation axis (single-qubit gates)
    rotation: Optional[float] = None                 # rotation angle in radians
    # Optional "pretty" factorisation used only for display, so the UI can
    # print H as (1/sqrt 2)[[1, 1], [1, -1]] instead of 0.7071...
    display_matrix: Optional[Matrix] = None
    display_scale: float = 1.0
    display_scale_latex: str = ""
    color: str = "#6C5CE7"                           # colour of the gate box in the UI

    def __post_init__(self) -> None:
        if self.matrix.size != 2 ** self.arity:
            raise ValueError(f"{self.symbol}: a {self.arity}-qubit gate needs a {2 ** self.arity}x{2 ** self.arity} matrix")

    @property
    def shown_matrix(self) -> Matrix:
        return self.display_matrix if self.display_matrix is not None else self.matrix

    @property
    def is_rotation(self) -> bool:
        return self.axis is not None and self.rotation is not None


def controlled(gate: Gate, *, name: str, symbol: str, description: str, color: str) -> Gate:
    """Build the controlled version of a gate: apply `gate` only when the
    control qubit is |1>. The first target of the resulting gate is the control.
    """
    size = gate.matrix.size
    rows = []
    for i in range(2 * size):
        row = []
        for j in range(2 * size):
            if i < size and j < size:
                row.append(ONE if i == j else ZERO)          # control = |0>: identity
            elif i >= size and j >= size:
                row.append(gate.matrix.rows[i - size][j - size])  # control = |1>: the gate
            else:
                row.append(ZERO)
        rows.append(tuple(row))
    return Gate(name=name, symbol=symbol, matrix=Matrix(tuple(rows)), description=description,
                arity=gate.arity + 1, color=color)


# --- single-qubit gates ------------------------------------------------------
X = Gate(
    name="Pauli-X",
    symbol="X",
    matrix=Matrix2x2(ZERO, ONE, ONE, ZERO),
    description="Bit flip: swaps the amplitudes of |0> and |1> (the quantum NOT gate).",
    axis=(1.0, 0.0, 0.0),
    rotation=math.pi,
    color="#E4572E",
)

Y = Gate(
    name="Pauli-Y",
    symbol="Y",
    matrix=Matrix2x2(ZERO, -I, I, ZERO),
    description="Bit flip and phase flip together: |0> -> i|1> and |1> -> -i|0>.",
    axis=(0.0, 1.0, 0.0),
    rotation=math.pi,
    color="#F59E0B",
)

Z = Gate(
    name="Pauli-Z",
    symbol="Z",
    matrix=Matrix2x2(ONE, ZERO, ZERO, -ONE),
    description="Phase flip: leaves |0> alone and multiplies |1> by -1.",
    axis=(0.0, 0.0, 1.0),
    rotation=math.pi,
    color="#5B6CFF",
)

H = Gate(
    name="Hadamard",
    symbol="H",
    matrix=Matrix2x2(
        Complex(INV_SQRT2), Complex(INV_SQRT2),
        Complex(INV_SQRT2), Complex(-INV_SQRT2),
    ),
    description="Creates superposition: maps |0> to |+> and |1> to |->.",
    axis=(INV_SQRT2, 0.0, INV_SQRT2),
    rotation=math.pi,
    display_matrix=Matrix2x2(ONE, ONE, ONE, -ONE),
    display_scale=INV_SQRT2,
    display_scale_latex=r"\frac{1}{\sqrt{2}}",
    color="#0EA5A4",
)

S = Gate(
    name="Phase (S)",
    symbol="S",
    matrix=Matrix2x2(ONE, ZERO, ZERO, I),
    description="Quarter-turn phase: multiplies |1> by i (S = sqrt(Z)).",
    axis=(0.0, 0.0, 1.0),
    rotation=math.pi / 2,
    color="#8B5CF6",
)

T = Gate(
    name="T (pi/8)",
    symbol="T",
    matrix=Matrix2x2(ONE, ZERO, ZERO, Complex.exp_i(math.pi / 4)),
    description="Eighth-turn phase: multiplies |1> by e^(i pi/4) (T = sqrt(S)).",
    axis=(0.0, 0.0, 1.0),
    rotation=math.pi / 4,
    color="#EC4899",
)

# --- two-qubit gates ---------------------------------------------------------
CNOT = controlled(
    X, name="Controlled-NOT", symbol="CNOT",
    description="Flips the target qubit when the control qubit is |1>. Creates entanglement from superposition.",
    color="#334155",
)

CZ = controlled(
    Z, name="Controlled-Z", symbol="CZ",
    description="Applies a phase of -1 only to |11>. Symmetric: either qubit can be called the control.",
    color="#0369A1",
)

SWAP = Gate(
    name="Swap",
    symbol="SWAP",
    matrix=Matrix((
        (ONE, ZERO, ZERO, ZERO),
        (ZERO, ZERO, ONE, ZERO),
        (ZERO, ONE, ZERO, ZERO),
        (ZERO, ZERO, ZERO, ONE),
    )),
    description="Exchanges the states of the two qubits.",
    arity=2,
    color="#0F766E",
)

SINGLE_QUBIT_GATES: List[str] = ["H", "X", "Y", "Z", "S", "T"]
TWO_QUBIT_GATES: List[str] = ["CNOT", "CZ", "SWAP"]
GATE_ORDER: List[str] = SINGLE_QUBIT_GATES + TWO_QUBIT_GATES
GATES: Dict[str, Gate] = {g.symbol: g for g in (H, X, Y, Z, S, T, CNOT, CZ, SWAP)}


def get_gate(symbol: str) -> Gate:
    try:
        return GATES[symbol]
    except KeyError:
        raise KeyError(f"Unknown gate '{symbol}'. Supported gates: {GATE_ORDER}") from None
