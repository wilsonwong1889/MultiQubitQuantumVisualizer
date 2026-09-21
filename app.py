"""Qubit Visualizer — see how quantum gates transform qubits.

Run with:  streamlit run app.py

The app stores only the register setup (how many qubits, what each starts
in), the list of operations, and the current step (see model.py). On every
rerun it asks the quantum engine for the state after each operation and every
panel is derived from the state at the current step, so the circuit, ket,
vector, matrix calculation, probabilities and Bloch spheres can never disagree.
"""
from __future__ import annotations

import streamlit as st

import model
from components import (
    bloch_sphere,
    circuit,
    controls,
    explanation,
    gate_panel,
    matrix_calculation,
    measurement_panel,
    state_panel,
    theme,
    toolbar,
)
from components.widgets import section
from quantum.bloch import bloch_vector
from quantum.circuit import simulate_circuit
from quantum.state import BELL_STATES, NAMED_STATES
from utils.format_state import complex_latex, coordinate_text

st.set_page_config(page_title="Qubit Visualizer", page_icon="⚛️", layout="wide",
                   initial_sidebar_state="collapsed")


def header() -> None:
    c_title, c_badge = st.columns([4, 1], vertical_alignment="center")
    with c_title:
        st.title("⚛️ Qubit Visualizer")
        st.caption("See how quantum gates transform qubits — visually, algebraically, and on the Bloch sphere. "
                   "Build a circuit, then step through it one gate at a time.")


def reference_expanders() -> None:
    with st.expander("Bloch sphere reference"):
        st.markdown(
            "For a single qubit $|\\psi\\rangle = \\alpha|0\\rangle + \\beta|1\\rangle$ the Bloch vector is computed "
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
                f"| {name} | $\\alpha = {complex_latex(named.alpha)},\\ \\beta = {complex_latex(named.beta)}$ | "
                f"({coordinate_text(x)}, {coordinate_text(y)}, {coordinate_text(z)}) |"
            )
        st.markdown("\n".join(rows))
        st.markdown(
            "For a qubit inside a larger register the same formula is applied to its **reduced density matrix** "
            "$\\rho = \\mathrm{Tr}_{\\text{others}}|\\psi\\rangle\\langle\\psi|$. If the qubit is entangled with the "
            "others, $\\rho$ is mixed and the arrow is shorter than 1 — at maximal entanglement it vanishes."
        )
        st.markdown("**Bell states** (maximally entangled pairs): " + ", ".join(
            f"${latex} = {'(' + ('|00\\rangle' if 'Phi' in latex else '|01\\rangle') + (' + ' if '+' in latex else ' - ') + ('|11\\rangle' if 'Phi' in latex else '|10\\rangle') + ')/\\sqrt{2}'}$"
            for _name, latex, _state in BELL_STATES
        ))
    with st.expander("About this project"):
        st.markdown(
            "**Qubit Visualizer** was made by **Wilson Wong**, an undergraduate in Computer Science researching "
            "quantum computing, as a teaching tool for a Quantum Algorithms course. Pick initial states, "
            "add gates, and step through the circuit: the circuit, state vector, ket notation, gate matrix, "
            "matrix multiplication, measurement probabilities and Bloch spheres all update from the same "
            "underlying state.\n\n"
            "Implementation: a dependency-free Python quantum engine (`quantum/`) that simulates any number of "
            "qubits, a Streamlit UI (`components/`), Plotly for the 3D Bloch spheres, and `pytest` tests "
            "(`tests/`) that verify the mathematics independently of the interface. See `docs/EXTENDING.md` "
            "for how to add gates, qubits or measurements."
        )


def footer() -> None:
    st.divider()
    st.markdown(
        "<div style='text-align:center;color:#64748B;font-size:0.9rem;line-height:1.6;padding:0.4rem 0 1rem 0'>"
        "Made by <strong>Wilson Wong</strong> — undergraduate in Computer Science, researching quantum computing.<br>"
        "Qubit Visualizer · a Quantum Algorithms course project · "
        "<a href='https://github.com/wilsonwong1889/QuantumVisualizer' target='_blank' style='color:#6C5CE7'>source on GitHub</a>"
        "</div>",
        unsafe_allow_html=True,
    )


def main() -> None:
    model.init_session()
    theme.inject()
    header()

    toolbar.render()

    # Derive everything for the current step from the engine.
    circ = model.current_circuit()
    states = simulate_circuit(circ)
    step = min(st.session_state.step, len(circ.operations))
    current = states[step]
    previous = states[step - 1] if step > 0 else None
    op = circ.operations[step - 1] if step > 0 else None

    with st.container(border=True):
        section("🔌", "Quantum circuit", "Click a step in the timeline (or use Previous / Next) to inspect that point in the circuit.")
        circuit.render(circ, step)
        controls.render(step, len(circ.operations))
        if st.session_state.preset_note:
            st.info(st.session_state.preset_note, icon="📚")

    left, right = st.columns([1, 1], gap="medium")
    with left:
        with st.container(border=True):
            state_panel.render(current, step)
        with st.container(border=True):
            if op is not None and previous is not None:
                matrix_calculation.render(previous, op, current, step)
                st.divider()
                explanation.render(previous, op, current)
            else:
                section("🔁", "Transformation")
                st.caption(
                    "No gate has been applied yet at this step. Add a gate or press Next ▶ to see the matrix "
                    "multiplication that transforms the state."
                )
    with right:
        with st.container(border=True):
            bloch_sphere.render(current, previous, op)
        with st.container(border=True):
            measurement_panel.render(current)

    with st.container(border=True):
        gate_panel.render(op.gate_object if op is not None else None)
    reference_expanders()
    footer()


if __name__ == "__main__":  # Streamlit runs the script as __main__
    main()
