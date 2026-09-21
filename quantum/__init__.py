"""Quantum engine for the Qubit Visualizer.

Everything in this package is plain Python with no UI dependencies, so the
Streamlit app (and the tests) simply ask the engine for a new state and then
derive whatever they need to display from it.
"""
from .complex_number import Complex, ZERO, ONE, I
from .matrix import Matrix2x2, IDENTITY
from .gates import Gate, GATES, GATE_ORDER, H, X, Y, Z, get_gate
from .qubit import (
    QubitState,
    INITIAL_STATES,
    INITIAL_STATE_LABELS,
    NAMED_STATES,
    apply_gate,
    simulate,
)
from .bloch import bloch_vector, rotate_about_axis, rotation_path

__all__ = [
    "Complex", "ZERO", "ONE", "I",
    "Matrix2x2", "IDENTITY",
    "Gate", "GATES", "GATE_ORDER", "H", "X", "Y", "Z", "get_gate",
    "QubitState", "INITIAL_STATES", "INITIAL_STATE_LABELS", "NAMED_STATES",
    "apply_gate", "simulate",
    "bloch_vector", "rotate_about_axis", "rotation_path",
]
