"""The Bell-state lesson view."""
from __future__ import annotations

import streamlit as st

import model
from components.circuit import circuit_svg
from components.widgets import section
from data.lesson import BELL_RECIPES, SECTIONS, bell_circuit
from quantum.bloch import bloch_vector, length
from utils.format_state import ket_vert, table_cell


def _circuit_preview(spec) -> None:
    """A small, non-interactive picture of the circuit the section is about."""
    circ = spec.to_circuit()
    st.markdown(
        f'<div style="overflow-x:auto;padding:2px 0 6px 0;opacity:.95">'
        f'{circuit_svg(circ, len(circ.operations))}</div>',
        unsafe_allow_html=True,
    )


def _bell_table() -> None:
    rows = ["| Bell state | Definition | Start from | Outcomes |", "|---|---|---|---|"]
    for name, latex, initial in BELL_RECIPES:
        state = bell_circuit(initial).final_state()
        nonzero = [label for label, p in zip(state.basis_labels(), state.probabilities()) if p > 1e-9]
        correlation = "always agree" if all(l[0] == l[1] for l in nonzero) else "always disagree"
        rows.append(
            f"| **{table_cell(name)}** | ${latex.replace('|', chr(92) + 'vert ')}$ | "
            f"${ket_vert(initial[0] + initial[1])}$ | "
            f"{' or '.join(table_cell(f'|{l}⟩') for l in nonzero)} — {correlation} |"
        )
    st.markdown("\n".join(rows))


def _section(sec, index: int, total: int) -> None:
    with st.container(border=True):
        section(sec.icon, f"{index}. {sec.title}")
        st.markdown(sec.body)
        for equation in sec.equations:
            st.latex(equation)
        if sec.key == "four":
            _bell_table()
        if sec.circuit is not None:
            _circuit_preview(sec.circuit)
            st.button(
                f"▶ {sec.try_it_label}", key=f"lesson_try_{sec.key}",
                on_click=model.load_circuit_spec,
                args=(sec.circuit, f"**From the lesson — {sec.title}.** {sec.takeaway}"),
                help="Loads this circuit in the Explore view so you can step through it.",
            )
        if sec.takeaway:
            st.success(f"**Takeaway:** {sec.takeaway}", icon="🔑")


def render() -> None:
    st.markdown("## 📘 Lesson: Bell states")
    st.caption(
        "The four maximally entangled two-qubit states — how to build them, why they cannot be "
        "taken apart, and what happens when you measure them. Every circuit here opens in the "
        "Explore view so you can watch it happen."
    )

    phi_plus = bell_circuit(("0", "0")).final_state()
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Bell states", "4", help="They form an orthonormal basis for the two-qubit space.")
    with c2:
        st.metric("Gates needed", "2", help="One Hadamard and one CNOT.")
    with c3:
        st.metric("Bloch arrow length", f"{length(bloch_vector(phi_plus, 0)):.2f}",
                  help="Each qubit of a Bell pair has no state of its own.")

    for i, sec in enumerate(SECTIONS, start=1):
        _section(sec, i, len(SECTIONS))

    with st.container(border=True):
        section("✏️", "Check your understanding",
                "Ten questions on Bell states, entanglement and measurement — with worked solutions.")
        st.button("Go to the practice questions →", key="lesson_to_practice",
                  on_click=model.go_to, args=(model.PRACTICE,), type="primary")
