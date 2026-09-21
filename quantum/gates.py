"""The single-qubit gates supported in Version 1: X, Y, Z and H.

Every gate is a 180-degree rotation of the Bloch sphere about some axis, so
each one records that axis and angle; the UI uses them to animate the arrow.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from .complex_number import Complex, I, ONE, ZERO
from .matrix import Matrix2x2

INV_SQRT2 = 1.0 / math.sqrt(2.0)


@dataclass(frozen=True)
class Gate:
    name: str
    symbol: str
    matrix: Matrix2x2
    description: str
    axis: Tuple[float, float, float]   # unit vector on the Bloch sphere
    rotation: float                    # rotation angle in radians
    # Optional "pretty" factorisation used only for display, so the UI can
    # print H as (1/sqrt 2)[[1, 1], [1, -1]] instead of 0.7071...
    display_matrix: Optional[Matrix2x2] = None
    display_scale: float = 1.0
    display_scale_latex: str = ""

    @property
    def shown_matrix(self) -> Matrix2x2:
        return self.display_matrix if self.display_matrix is not None else self.matrix


X = Gate(
    name="Pauli-X",
    symbol="X",
    matrix=Matrix2x2(ZERO, ONE, ONE, ZERO),
    description="Bit flip: swaps the amplitudes of |0> and |1> (the quantum NOT gate).",
    axis=(1.0, 0.0, 0.0),
    rotation=math.pi,
)

Y = Gate(
    name="Pauli-Y",
    symbol="Y",
    matrix=Matrix2x2(ZERO, -I, I, ZERO),
    description="Bit flip and phase flip together: |0> -> i|1> and |1> -> -i|0>.",
    axis=(0.0, 1.0, 0.0),
    rotation=math.pi,
)

Z = Gate(
    name="Pauli-Z",
    symbol="Z",
    matrix=Matrix2x2(ONE, ZERO, ZERO, -ONE),
    description="Phase flip: leaves |0> alone and multiplies |1> by -1.",
    axis=(0.0, 0.0, 1.0),
    rotation=math.pi,
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
)

GATES: Dict[str, Gate] = {"H": H, "X": X, "Y": Y, "Z": Z}
GATE_ORDER: List[str] = ["H", "X", "Y", "Z"]


def get_gate(symbol: str) -> Gate:
    try:
        return GATES[symbol]
    except KeyError:
        raise KeyError(f"Unknown gate '{symbol}'. Supported gates: {GATE_ORDER}") from None
