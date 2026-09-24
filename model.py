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

EXPLORE, LESSON, PRACTICE = "🔬 Explore", "📘 Learn", "✏️ Practice"
VIEWS = [EXPLORE, LESSON, PRACTICE]


def ss():
    return st.session_state


def init_session() -> None:
    s = ss()
    s.setdefault("num_qubits", 1)
    s.setdefault("ops", [])            # list of (symbol, targets)
    s.setdefault("step", 0)
    s.setdefault("preset_note", None)
    s.setdefault("measurement", None)
    s.setdefault("view", VIEWS[0])
    s.setdefault("answers", {})        # question key -> chosen option
    s.setdefault("checked", set())     # question keys the student has submitted
    s.setdefault("active_module", "qubits")
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


def go_to(view: str) -> None:
    s = ss()
    s.view = view
    s["__view_last"] = view


def load_circuit_spec(spec, note: str = "", *, switch_to_explore: bool = True) -> None:
    """Load a CircuitSpec from the lesson or a practice question into Explore."""
    s = ss()
    s.num_qubits = spec.num_qubits
    s.qubit_count = spec.num_qubits
    s["__qubit_count_last"] = spec.num_qubits
    for q, key in enumerate(spec.initial):
        s[f"init_{q}"] = key
        s[f"__init_{q}_last"] = key
    s.ops = [(sym, tuple(t)) for sym, t in spec.operations]
    set_step(len(s.ops))
    s.measurement = None
    s.preset_note = note or None
    if switch_to_explore:
        go_to(EXPLORE)


# --- practice answers ----------------------------------------------------------------
def record_answer(question_key: str) -> None:
    """Remember the chosen option and mark the question as submitted."""
    s = ss()
    s.answers = {**s.answers, question_key: s.get(f"choice_{question_key}")}
    s.checked = set(s.checked) | {question_key}


def clear_answer(question_key: str) -> None:
    s = ss()
    s.answers = {k: v for k, v in s.answers.items() if k != question_key}
    s.checked = set(s.checked) - {question_key}
    s[f"choice_{question_key}"] = None


def reset_practice() -> None:
    s = ss()
    for key in list(s.answers):
        s[f"choice_{key}"] = None
    s.answers = {}
    s.checked = set()


def _score_over(keys):
    s = ss()
    from data.practice import QUESTIONS_BY_KEY
    answered = [k for k in keys if k in s.checked]
    correct = sum(1 for k in answered if QUESTIONS_BY_KEY[k].is_correct(s.answers.get(k)))
    return correct, len(answered)


def practice_score():
    """(number correct, number answered) over the whole question set."""
    from data.practice import QUESTIONS_BY_KEY
    return _score_over(QUESTIONS_BY_KEY)


def module_score(module_key: str):
    """(number correct, number answered) within one curriculum module."""
    from data.practice import questions_for
    return _score_over([q.key for q in questions_for(module_key)])


def reset_module(module_key: str) -> None:
    from data.practice import questions_for
    s = ss()
    keys = {q.key for q in questions_for(module_key)}
    for key in keys:
        s[f"choice_{key}"] = None
    s.answers = {k: v for k, v in s.answers.items() if k not in keys}
    s.checked = set(s.checked) - keys


def go_to_lesson(module_key: str) -> None:
    """Open the Learn view on a particular module."""
    go_to(LESSON)
    ss().active_module = module_key


def go_to_practice(module_key: str) -> None:
    go_to(PRACTICE)
    ss().active_module = module_key


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
