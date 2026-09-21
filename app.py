"""Qubit Visualizer — see how quantum gates transform a qubit.

Run with:  streamlit run app.py

The app stores only three things (section 16 of the plan): the initial state,
the list of gates, and the current step. Everything on screen is derived from
the quantum engine's state for that step, so the circuit, ket, vector,
matrix calculation, probabilities and Bloch sphere can never disagree.
"""
from __future__ import annotations

import streamlit as st

from components import (
    bloch_sphere,
    circuit,
    controls,
    explanation,
    gate_panel,
    matrix_calculation,
    probability_panel,
    state_panel,
)
from data.presets import PRESETS, Preset
from quantum.gates import GATE_ORDER, GATES, get_gate
from quantum.qubit import INITIAL_STATE_LABELS, INITIAL_STATES, NAMED_STATES, simulate
from quantum.bloch import bloch_vector
from utils.format_state import complex_latex, coordinate_text

MAX_GATES = 10

st.set_page_config(page_title="Qubit Visualizer", page_icon="⚛️", layout="wide")


# --- application state -------------------------------------------------------
def init_session() -> None:
    ss = st.session_state
    ss.setdefault("initial", "0")       # key into INITIAL_STATES
    ss.setdefault("gates", [])          # list of gate symbols
    ss.setdefault("step", 0)            # 0 = initial state, k = after gate k
    ss.setdefault("preset_note", None)


def add_gate(symbol: str) -> None:
    ss = st.session_state
    if len(ss.gates) >= MAX_GATES:
        return
    ss.gates.append(symbol)
    ss.step = len(ss.gates)            # jump to the newly applied gate
    ss.preset_note = None


def undo_gate() -> None:
    ss = st.session_state
    if ss.gates:
        ss.gates.pop()
    ss.step = min(ss.step, len(ss.gates))
    ss.preset_note = None


def reset_circuit() -> None:
    ss = st.session_state
    ss.gates = []
    ss.step = 0
    ss.preset_note = None


def previous_step() -> None:
    st.session_state.step = max(0, st.session_state.step - 1)


def next_step() -> None:
    ss = st.session_state
    ss.step = min(len(ss.gates), ss.step + 1)


def go_to_step(step: int) -> None:
    st.session_state.step = step


def load_preset(preset: Preset) -> None:
    ss = st.session_state
    ss.initial = preset.initial
    ss.gates = list(preset.gates)
    ss.step = len(preset.gates)
    ss.preset_note = f"**{preset.label}** — {preset.concept}"


def clear_note() -> None:
    st.session_state.preset_note = None


# --- page ---------------------------------------------------------------------
def main() -> None:
    init_session()
    ss = st.session_state

    st.markdown(
        "<style>.katex-display { overflow-x: auto; overflow-y: hidden; padding: 2px 0; }</style>",
        unsafe_allow_html=True,
    )
    st.title("⚛️ Qubit Visualizer")
    st.caption("See how quantum gates transform a qubit — visually, algebraically, and on the Bloch sphere.")

    # Top rows: initial state + gate buttons, then preset examples
    c_initial, c_gates = st.columns([1, 1.2], gap="large")
    with c_initial:
        st.radio(
            "Initial state", options=list(INITIAL_STATES),
            format_func=lambda key: INITIAL_STATE_LABELS[key],
            horizontal=True, key="initial", on_change=clear_note,
        )
    with c_gates:
        st.markdown("Add gate")
        full = len(ss.gates) >= MAX_GATES
        for col, symbol in zip(st.columns(len(GATE_ORDER)), GATE_ORDER):
            with col:
                st.button(
                    symbol, key=f"add_{symbol}", on_click=add_gate, args=(symbol,),
                    help=GATES[symbol].description, disabled=full, width="stretch",
                )
        if full:
            st.caption(f"Maximum of {MAX_GATES} gates reached.")
    st.markdown("Preset examples")
    for col, preset in zip(st.columns(len(PRESETS)), PRESETS):
        with col:
            st.button(
                preset.label, key=f"preset_{preset.key}", on_click=load_preset,
                args=(preset,), help=preset.concept, width="stretch",
            )

    # Derive everything for the current step from the engine.
    initial = INITIAL_STATES[ss.initial]
    gates = [get_gate(symbol) for symbol in ss.gates]
    states = simulate(initial, gates)
    step = min(ss.step, len(gates))
    current = states[step]
    previous = states[step - 1] if step > 0 else None
    gate = gates[step - 1] if step > 0 else None

    st.divider()
    circuit.render(INITIAL_STATE_LABELS[ss.initial], ss.gates, step, go_to_step)
    controls.render(step, len(gates), previous_step, next_step, undo_gate, reset_circuit)
    if ss.preset_note:
        st.info(ss.preset_note, icon="📚")
    st.divider()

    left, right = st.columns([1, 1], gap="large")
    with left:
        state_panel.render(current, step)
        probability_panel.render(current)
        st.divider()
        if gate is not None and previous is not None:
            matrix_calculation.render(previous, gate, current, step)
            st.divider()
            explanation.render(previous, gate, current)
        else:
            st.markdown("**Transformation**")
            st.caption(
                "No gate has been applied yet at this step. Add a gate (H, X, Y or Z) or press "
                "Next ▶ to see the matrix multiplication that transforms the state."
            )
    with right:
        bloch_sphere.render(current, previous, gate)
        bloch_sphere.render_coordinates(current, previous)
        st.divider()
        gate_panel.render(gate)

    st.divider()
    with st.expander("Bloch sphere reference"):
        st.markdown(
            "For $|\\psi\\rangle = \\alpha|0\\rangle + \\beta|1\\rangle$ the Bloch vector is computed "
            "directly from the amplitudes ($\\alpha^{*}$ is the complex conjugate of $\\alpha$):"
        )
        st.latex(
            r"x = 2\,\mathrm{Re}(\alpha^{*}\beta), \qquad y = 2\,\mathrm{Im}(\alpha^{*}\beta), "
            r"\qquad z = |\alpha|^2 - |\beta|^2"
        )
        rows = ["| State | α, β | Bloch coordinates (x, y, z) |", "|---|---|---|"]
        for name, _latex, named in NAMED_STATES:
            x, y, z = bloch_vector(named)
            rows.append(
                f"| {name} | ${_latex_amplitudes(named)}$ | "
                f"({coordinate_text(x)}, {coordinate_text(y)}, {coordinate_text(z)}) |"
            )
        st.markdown("\n".join(rows))
        st.caption(
            "Every gate in this app is a 180° rotation of the sphere about some axis: X, Y and Z "
            "rotate about their own axis, and H rotates about the diagonal between x and z."
        )

    with st.expander("About this project"):
        st.markdown(
            "**Qubit Visualizer** is a Version 1 single-qubit teaching tool built for a Quantum "
            "Algorithms course. Pick an initial state, add gates, and step through the circuit: "
            "the circuit, state vector, ket notation, gate matrix, matrix multiplication, "
            "measurement probabilities and Bloch sphere all update from the same underlying state.\n\n"
            "Implementation: a dependency-free Python quantum engine (`quantum/`), a Streamlit UI "
            "(`components/`), Plotly for the 3D Bloch sphere, and `pytest` tests (`tests/`) that "
            "verify the mathematics independently of the interface."
        )


def _latex_amplitudes(state) -> str:
    return rf"\alpha = {complex_latex(state.alpha)},\ \beta = {complex_latex(state.beta)}"


if __name__ == "__main__":  # Streamlit runs the script as __main__
    main()
