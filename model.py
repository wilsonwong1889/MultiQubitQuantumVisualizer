"""Session-state model and the callbacks that change it.

Only three kinds of things are stored: how many qubits there are (and what
each starts in), the list of operations, and which step is being inspected.
Everything on screen is derived from the circuit for the current step.
"""
from __future__ import annotations

import streamlit as st

from data.presets import Preset
from quantum.circuit import Circuit, Operation
from quantum.gates import get_gate
from quantum.state import INITIAL_STATES

MAX_QUBITS = 3
MAX_OPERATIONS = 12
QUBIT_OPTIONS = [1, 2, 3]
SHOT_OPTIONS = [1, 10, 100, 1000]


def ss():
    return st.session_state


def init_session() -> None:
    s = ss()
    s.setdefault("num_qubits", 1)
    s.setdefault("ops", [])            # list of (symbol, targets)
    s.setdefault("step", 0)
    s.setdefault("preset_note", None)
    s.setdefault("measurement", None)
    for q in range(MAX_QUBITS):
        s.setdefault(f"init_{q}", "0")


# --- derived values ------------------------------------------------------------
def initial_keys() -> tuple:
    s = ss()
    return tuple((s.get(f"init_{q}") or "0") for q in range(s.num_qubits))


def current_circuit() -> Circuit:
    s = ss()
    return Circuit(s.num_qubits, initial_keys(), tuple(Operation(sym, tuple(t)) for sym, t in s.ops))


def signature() -> tuple:
    """Identifies 'the state being looked at' so measurement results can be invalidated."""
    s = ss()
    return (s.num_qubits, initial_keys(), tuple((sym, tuple(t)) for sym, t in s.ops), s.step)


# --- step navigation -------------------------------------------------------------
def set_step(step: int) -> None:
    s = ss()
    step = max(0, min(step, len(s.ops)))
    s.step = step
    s.step_control = step
    s["__step_control_last"] = step


def previous_step() -> None:
    set_step(ss().step - 1)


def next_step() -> None:
    set_step(ss().step + 1)


def sync_step_from_control() -> None:
    value = ss().get("step_control")
    if value is not None:
        set_step(value)


# --- editing the circuit ------------------------------------------------------------
def _touch() -> None:
    s = ss()
    s.preset_note = None
    s.measurement = None


def set_num_qubits() -> None:
    s = ss()
    n = s.get("qubit_count") or s.num_qubits
    if n != s.num_qubits:
        s.num_qubits = n
        s.ops = []                     # operations refer to qubit indices, so start over
        set_step(0)
        _touch()


def add_operation(symbol: str, targets: tuple) -> None:
    s = ss()
    if len(s.ops) >= MAX_OPERATIONS:
        return
    gate = get_gate(symbol)
    if len(targets) != gate.arity or len(set(targets)) != len(targets):
        return
    s.ops.append((symbol, tuple(targets)))
    set_step(len(s.ops))              # jump to the newly applied gate
    _touch()


def add_single_qubit_gate(symbol: str) -> None:
    add_operation(symbol, (ss().get("target") or 0,))


def add_two_qubit_gate(symbol: str) -> None:
    s = ss()
    add_operation(symbol, (s.get("ctrl") or 0, s.get("tgt") if s.get("tgt") is not None else 1))


def undo_operation() -> None:
    s = ss()
    if s.ops:
        s.ops.pop()
    set_step(min(s.step, len(s.ops)))
    _touch()


def reset_circuit() -> None:
    ss().ops = []
    set_step(0)
    _touch()


def on_initial_state_change() -> None:
    _touch()


def load_preset(preset: Preset) -> None:
    s = ss()
    s.num_qubits = preset.num_qubits
    s.qubit_count = preset.num_qubits
    s["__qubit_count_last"] = preset.num_qubits
    for q, key in enumerate(preset.initial):
        s[f"init_{q}"] = key
        s[f"__init_{q}_last"] = key
    s.ops = [(sym, tuple(t)) for sym, t in preset.operations]
    set_step(len(s.ops))
    s.measurement = None
    s.preset_note = f"**{preset.label}** — {preset.concept}"


def load_selected_preset() -> None:
    from data.presets import PRESETS
    s = ss()
    key = s.get("preset_select")
    s.preset_select = None            # keep the dropdown showing its placeholder
    for preset in PRESETS:
        if preset.key == key:
            load_preset(preset)
            return


# --- measurement --------------------------------------------------------------------
def run_measurement() -> None:
    """Sample the state at the current step with the currently selected number of shots."""
    from quantum.circuit import simulate_circuit
    from quantum.measurement import measure_once, sample
    s = ss()
    shots = s.get("shots") or 100
    circuit = current_circuit()
    state = simulate_circuit(circuit)[min(s.step, len(circuit.operations))]
    if shots == 1:
        outcome, collapsed = measure_once(state)
        s.measurement = {"signature": signature(), "shots": 1, "outcome": outcome, "collapsed": collapsed}
    else:
        s.measurement = {"signature": signature(), "shots": shots, "counts": sample(state, shots)}
