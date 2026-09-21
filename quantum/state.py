"""Pure quantum states of one or more qubits, and gate application.

A state of n qubits is a vector of 2**n complex amplitudes. Basis states are
labelled by bit strings; qubit 0 is the LEFTMOST bit of the label, so for two
qubits the amplitudes are ordered |00>, |01>, |10>, |11>.

The application stores only the initial states and the list of operations;
every displayed quantity (ket, vector, probabilities, Bloch coordinates) is
derived from the QuantumState returned here so the panels can never disagree.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

from .complex_number import Complex, ONE, TOLERANCE, ZERO
from .gates import INV_SQRT2, Gate
from .matrix import Matrix


@dataclass(frozen=True)
class QuantumState:
    """|psi> = sum_k amplitudes[k] |k>, with sum |amplitude|^2 = 1."""

    amplitudes: Tuple[Complex, ...]

    def __post_init__(self) -> None:
        amps = tuple(self.amplitudes)
        n = len(amps)
        if n < 2 or n & (n - 1):
            raise ValueError("A state vector needs 2**num_qubits amplitudes")
        object.__setattr__(self, "amplitudes", amps)

    # --- shape ------------------------------------------------------------
    @property
    def dimension(self) -> int:
        return len(self.amplitudes)

    @property
    def num_qubits(self) -> int:
        return self.dimension.bit_length() - 1

    def basis_labels(self) -> List[str]:
        return [format(i, f"0{self.num_qubits}b") for i in range(self.dimension)]

    def bit(self, index: int, qubit: int) -> int:
        """Value of `qubit` in basis state number `index` (qubit 0 = leftmost)."""
        return (index >> (self.num_qubits - 1 - qubit)) & 1

    # --- single-qubit conveniences (alpha|0> + beta|1>) ----------------------
    @property
    def alpha(self) -> Complex:
        self._require_single_qubit()
        return self.amplitudes[0]

    @property
    def beta(self) -> Complex:
        self._require_single_qubit()
        return self.amplitudes[1]

    def _require_single_qubit(self) -> None:
        if self.num_qubits != 1:
            raise AttributeError("alpha/beta only exist for a single qubit; use .amplitudes")

    # --- amplitudes and probabilities ------------------------------------
    def as_vector(self) -> Tuple[Complex, ...]:
        return self.amplitudes

    def amplitude_of(self, label: str) -> Complex:
        return self.amplitudes[int(label, 2)]

    def probabilities(self) -> Tuple[float, ...]:
        """Born rule: P(k) = |amplitude_k|^2."""
        return tuple(a.magnitude_squared() for a in self.amplitudes)

    def probability_of(self, label: str) -> float:
        return self.amplitude_of(label).magnitude_squared()

    def norm_squared(self) -> float:
        return sum(self.probabilities())

    def is_normalized(self, tol: float = 1e-9) -> bool:
        return abs(self.norm_squared() - 1.0) < tol

    # --- comparisons ------------------------------------------------------
    def is_close(self, other: QuantumState, tol: float = TOLERANCE) -> bool:
        """Exact (phase-sensitive) comparison of the amplitudes."""
        return self.dimension == other.dimension and all(
            a.is_close(b, tol) for a, b in zip(self.amplitudes, other.amplitudes)
        )

    def global_phase_relative_to(self, other: QuantumState, tol: float = TOLERANCE) -> Optional[Complex]:
        """If self == phase * other for a unit-modulus phase, return that phase.

        X|-> = -|-> is the classic example: the amplitudes differ but the
        physical state (and the Bloch vector) is unchanged.
        """
        if self.dimension != other.dimension:
            return None
        reference = next((a for a in other.amplitudes if not a.is_zero(tol)), None)
        if reference is None:
            return None
        index = other.amplitudes.index(reference)
        phase = _divide(self.amplitudes[index], reference)
        if abs(phase.magnitude() - 1.0) > 1e-6:
            return None
        scaled = QuantumState(tuple(a * phase for a in other.amplitudes))
        return phase if self.is_close(scaled, 1e-6) else None

    def equals_up_to_global_phase(self, other: QuantumState, tol: float = TOLERANCE) -> bool:
        return self.global_phase_relative_to(other, tol) is not None

    # --- one qubit's view of a multi-qubit state ----------------------------
    def reduced_density_matrix(self, qubit: int) -> Matrix:
        """rho_ab = sum over the other qubits of psi[a, rest] * conj(psi[b, rest]).

        For a product state this is |phi><phi| of that qubit alone; for an
        entangled state it is mixed, and the qubit has no Bloch arrow of its own.
        """
        shift = self.num_qubits - 1 - qubit
        rho = [[ZERO, ZERO], [ZERO, ZERO]]
        for i, amp_i in enumerate(self.amplitudes):
            a = (i >> shift) & 1
            for b in (0, 1):
                j = (i & ~(1 << shift)) | (b << shift)
                rho[a][b] = rho[a][b] + amp_i * self.amplitudes[j].conjugate()
        return Matrix(tuple(tuple(row) for row in rho))

    def purity(self, qubit: int) -> float:
        """Tr(rho^2): 1 for a qubit with a definite state, 1/2 when maximally entangled."""
        rho = self.reduced_density_matrix(qubit)
        total = ZERO
        for a in (0, 1):
            for b in (0, 1):
                total = total + rho.rows[a][b] * rho.rows[b][a]
        return total.real

    def is_pure_on(self, qubit: int, tol: float = 1e-6) -> bool:
        return self.purity(qubit) > 1.0 - tol


def _divide(numerator: Complex, denominator: Complex) -> Complex:
    d = denominator.magnitude_squared()
    product = numerator * denominator.conjugate()
    return Complex(product.real / d, product.imag / d)


# --- constructors ------------------------------------------------------------
def QubitState(alpha: Complex, beta: Complex) -> QuantumState:  # noqa: N802 - reads like a type
    """Single-qubit state alpha|0> + beta|1>."""
    return QuantumState((alpha, beta))


def basis_state(label: str) -> QuantumState:
    """Computational basis state from a bit string, e.g. '0', '1', '01', '110'."""
    if not label or any(c not in "01" for c in label):
        raise ValueError(f"Basis label must be a non-empty bit string, got {label!r}")
    amps = [ZERO] * (2 ** len(label))
    amps[int(label, 2)] = ONE
    return QuantumState(tuple(amps))


def tensor(*states: QuantumState) -> QuantumState:
    """Tensor product |a> (x) |b> (x) ... -- independent qubits side by side."""
    if not states:
        raise ValueError("tensor() needs at least one state")
    amps: Tuple[Complex, ...] = (ONE,)
    for state in states:
        amps = tuple(a * b for a in amps for b in state.amplitudes)
    return QuantumState(amps)


# --- the named single-qubit states used throughout the UI --------------------
def ket0() -> QuantumState:
    return QubitState(ONE, ZERO)


def ket1() -> QuantumState:
    return QubitState(ZERO, ONE)


def ket_plus() -> QuantumState:
    return QubitState(Complex(INV_SQRT2), Complex(INV_SQRT2))


def ket_minus() -> QuantumState:
    return QubitState(Complex(INV_SQRT2), Complex(-INV_SQRT2))


def ket_plus_i() -> QuantumState:
    return QubitState(Complex(INV_SQRT2), Complex(0.0, INV_SQRT2))


def ket_minus_i() -> QuantumState:
    return QubitState(Complex(INV_SQRT2), Complex(0.0, -INV_SQRT2))


# Keys are what the app stores in session state; labels are what it shows.
INITIAL_STATES: Dict[str, QuantumState] = {
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
NAMED_STATES: List[Tuple[str, str, QuantumState]] = [
    ("|0⟩", r"|0\rangle", ket0()),
    ("|1⟩", r"|1\rangle", ket1()),
    ("|+⟩", r"|+\rangle", ket_plus()),
    ("|−⟩", r"|-\rangle", ket_minus()),
    ("|+i⟩", r"|{+i}\rangle", ket_plus_i()),
    ("|−i⟩", r"|{-i}\rangle", ket_minus_i()),
]


def _bell(a: str, b: str, sign: float) -> QuantumState:
    amps = [ZERO] * 4
    amps[int(a, 2)] = Complex(INV_SQRT2)
    amps[int(b, 2)] = Complex(sign * INV_SQRT2)
    return QuantumState(tuple(amps))


BELL_STATES: List[Tuple[str, str, QuantumState]] = [
    ("|Φ⁺⟩", r"|\Phi^{+}\rangle", _bell("00", "11", +1.0)),
    ("|Φ⁻⟩", r"|\Phi^{-}\rangle", _bell("00", "11", -1.0)),
    ("|Ψ⁺⟩", r"|\Psi^{+}\rangle", _bell("01", "10", +1.0)),
    ("|Ψ⁻⟩", r"|\Psi^{-}\rangle", _bell("01", "10", -1.0)),
]


# --- applying gates ----------------------------------------------------------
def validate_targets(gate: Gate, targets: Sequence[int], num_qubits: int) -> None:
    if len(targets) != gate.arity:
        raise ValueError(f"{gate.symbol} acts on {gate.arity} qubit(s) but got targets {tuple(targets)}")
    if len(set(targets)) != len(targets):
        raise ValueError(f"{gate.symbol}: target qubits must be distinct, got {tuple(targets)}")
    for t in targets:
        if not 0 <= t < num_qubits:
            raise ValueError(f"{gate.symbol}: qubit {t} is out of range for {num_qubits} qubit(s)")


def apply_gate(state: QuantumState, gate: Gate, targets: Optional[Sequence[int]] = None) -> QuantumState:
    """Apply `gate` to the given target qubits (default: qubits 0, 1, ...).

    For a controlled gate the first target is the control. The gate's matrix
    acts on the sub-index formed by the target bits (first target = most
    significant), leaving every other qubit untouched.
    """
    n = state.num_qubits
    if targets is None:
        targets = tuple(range(gate.arity))
    validate_targets(gate, targets, n)

    k = len(targets)
    shifts = [n - 1 - t for t in targets]     # bit position of each target
    rows = gate.matrix.rows
    amps = state.amplitudes
    new_amps = []
    for i in range(len(amps)):
        sub_index = 0                          # this basis state's bits on the targets
        base = i                               # ... and with those bits cleared
        for p, shift in enumerate(shifts):
            sub_index |= ((i >> shift) & 1) << (k - 1 - p)
            base &= ~(1 << shift)
        acc = ZERO
        for sub_col in range(2 ** k):
            m = rows[sub_index][sub_col]
            if m.is_zero():
                continue
            source = base
            for p, shift in enumerate(shifts):
                source |= ((sub_col >> (k - 1 - p)) & 1) << shift
            acc = acc + m * amps[source]
        new_amps.append(acc)
    return QuantumState(tuple(new_amps))


def full_operator(gate: Gate, targets: Sequence[int], num_qubits: int) -> Matrix:
    """The 2**n x 2**n matrix that `gate` on `targets` applies to the whole register."""
    dim = 2 ** num_qubits
    columns = []
    for j in range(dim):
        amps = [ZERO] * dim
        amps[j] = ONE
        columns.append(apply_gate(QuantumState(tuple(amps)), gate, targets).amplitudes)
    return Matrix(tuple(tuple(columns[j][i] for j in range(dim)) for i in range(dim)))


def simulate(initial: QuantumState, gates: Sequence[Gate]) -> List[QuantumState]:
    """Single-qubit convenience: states[0] is `initial`, states[k] applies gates[k-1]."""
    states = [initial]
    for gate in gates:
        states.append(apply_gate(states[-1], gate))
    return states
