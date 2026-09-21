"""Quantum engine for the Multi-Qubit Visualizer.

Everything in this package is plain Python with no UI dependencies, so the
Streamlit app (and the tests) simply ask the engine for a new state and then
derive whatever they need to display from it.
"""
from .complex_number import Complex, ZERO, ONE, I
from .matrix import Matrix, Matrix2x2, IDENTITY
from .gates import (
    Gate, GATES, GATE_ORDER, SINGLE_QUBIT_GATES, TWO_QUBIT_GATES,
    H, X, Y, Z, S, T, CNOT, CZ, SWAP, controlled, get_gate,
)
from .state import (
    QuantumState, QubitState, basis_state, tensor,
    INITIAL_STATES, INITIAL_STATE_LABELS, NAMED_STATES, BELL_STATES,
    apply_gate, full_operator, simulate,
)
from .circuit import Circuit, Operation, simulate_circuit
from .measurement import sample, collapse, measure_once, measure_qubit
from .bloch import bloch_vector, rotate_about_axis, rotation_path, straight_path

__all__ = [
    "Complex", "ZERO", "ONE", "I",
    "Matrix", "Matrix2x2", "IDENTITY",
    "Gate", "GATES", "GATE_ORDER", "SINGLE_QUBIT_GATES", "TWO_QUBIT_GATES",
    "H", "X", "Y", "Z", "S", "T", "CNOT", "CZ", "SWAP", "controlled", "get_gate",
    "QuantumState", "QubitState", "basis_state", "tensor",
    "INITIAL_STATES", "INITIAL_STATE_LABELS", "NAMED_STATES", "BELL_STATES",
    "apply_gate", "full_operator", "simulate",
    "Circuit", "Operation", "simulate_circuit",
    "sample", "collapse", "measure_once", "measure_qubit",
    "bloch_vector", "rotate_about_axis", "rotation_path", "straight_path",
]
