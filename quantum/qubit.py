"""Single-qubit pure states and gate application.

The application stores only the initial state and the list of gates; every
displayed quantity (ket, vector, probabilities, Bloch coordinates) is derived
from the QubitState returned here so the panels can never disagree.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

from .complex_number import Complex, I, ONE, TOLERANCE, ZERO
from .gates import INV_SQRT2, Gate


@dataclass(frozen=True)
class QubitState:
    """|psi> = alpha|0> + beta|1>, with |alpha|^2 + |beta|^2 = 1."""

    alpha: Complex
    beta: Complex

    def as_vector(self) -> Tuple[Complex, Complex]:
        return (self.alpha, self.beta)

    def probabilities(self) -> Tuple[float, float]:
        """Born rule: P(0) = |alpha|^2, P(1) = |beta|^2."""
        return (self.alpha.magnitude_squared(), self.beta.magnitude_squared())

    def norm_squared(self) -> float:
        p0, p1 = self.probabilities()
        return p0 + p1

    def is_normalized(self, tol: float = 1e-9) -> bool:
        return abs(self.norm_squared() - 1.0) < tol

    def is_close(self, other: QubitState, tol: float = TOLERANCE) -> bool:
        """Exact (phase-sensitive) comparison of the amplitudes."""
        return self.alpha.is_close(other.alpha, tol) and self.beta.is_close(other.beta, tol)

    def global_phase_relative_to(self, other: QubitState, tol: float = TOLERANCE) -> Optional[Complex]:
        """If self == phase * other for a unit-modulus phase, return that phase.

        X|-> = -|-> is the classic example: the amplitudes differ but the
        physical state (and the Bloch vector) is unchanged.
        """
        if not other.alpha.is_zero(tol):
            phase = _divide(self.alpha, other.alpha)
        elif not other.beta.is_zero(tol):
            phase = _divide(self.beta, other.beta)
        else:
            return None
        if abs(phase.magnitude() - 1.0) > 1e-6:
            return None
        scaled = QubitState(other.alpha * phase, other.beta * phase)
        return phase if self.is_close(scaled, 1e-6) else None

    def equals_up_to_global_phase(self, other: QubitState, tol: float = TOLERANCE) -> bool:
        return self.global_phase_relative_to(other, tol) is not None


def _divide(numerator: Complex, denominator: Complex) -> Complex:
    d = denominator.magnitude_squared()
    product = numerator * denominator.conjugate()
    return Complex(product.real / d, product.imag / d)


# --- the six named states used throughout the UI ----------------------------
def ket0() -> QubitState:
    return QubitState(ONE, ZERO)


def ket1() -> QubitState:
    return QubitState(ZERO, ONE)


def ket_plus() -> QubitState:
    return QubitState(Complex(INV_SQRT2), Complex(INV_SQRT2))


def ket_minus() -> QubitState:
    return QubitState(Complex(INV_SQRT2), Complex(-INV_SQRT2))


def ket_plus_i() -> QubitState:
    return QubitState(Complex(INV_SQRT2), Complex(0.0, INV_SQRT2))


def ket_minus_i() -> QubitState:
    return QubitState(Complex(INV_SQRT2), Complex(0.0, -INV_SQRT2))


# Keys are what the app stores in session state; labels are what it shows.
INITIAL_STATES: Dict[str, QubitState] = {
    "0": ket0(),
    "1": ket1(),
    "+": ket_plus(),
    "-": ket_minus(),
}

INITIAL_STATE_LABELS: Dict[str, str] = {
    "0": "|0⟩",
    "1": "|1⟩",
    "+": "|+⟩",
    "-": "|−⟩",
}

# (unicode label, LaTeX label, state) -- used to recognise a state by name.
NAMED_STATES: List[Tuple[str, str, QubitState]] = [
    ("|0⟩", r"|0\rangle", ket0()),
    ("|1⟩", r"|1\rangle", ket1()),
    ("|+⟩", r"|+\rangle", ket_plus()),
    ("|−⟩", r"|-\rangle", ket_minus()),
    ("|+i⟩", r"|{+i}\rangle", ket_plus_i()),
    ("|−i⟩", r"|{-i}\rangle", ket_minus_i()),
]


def apply_gate(state: QubitState, gate: Gate) -> QubitState:
    """Return gate.matrix . [alpha, beta]^T as a new state."""
    alpha, beta = gate.matrix.multiply_vector(state.as_vector())
    return QubitState(alpha, beta)


def simulate(initial: QubitState, gates: Sequence[Gate]) -> List[QubitState]:
    """states[0] is the initial state; states[k] is gates[k-1] applied to states[k-1]."""
    states = [initial]
    for gate in gates:
        states.append(apply_gate(states[-1], gate))
    return states
