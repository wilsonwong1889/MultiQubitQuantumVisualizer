"""Ket notation, vector notation and amplitudes (Phase 8 of the plan)."""
from __future__ import annotations

import streamlit as st

from components.widgets import section
from quantum.state import QuantumState
from utils.format_state import complex_latex, recognise_state, state_chain_aligned, vector_latex


def render(state: QuantumState, step: int) -> None:
    section("🧮", f"State after step {step}" if step else "Initial state")
    st.latex(state_chain_aligned(state, symbol=rf"|\psi_{{{step}}}\rangle"))
    if state.num_qubits == 1:
        st.latex(
            r"\begin{gathered} \begin{bmatrix} \alpha \\ \beta \end{bmatrix} = " + vector_latex(state.as_vector())
            + r" \\[4pt] \alpha = " + complex_latex(state.alpha)
            + r", \qquad \beta = " + complex_latex(state.beta)
            + r" \end{gathered}"
        )
    else:
        labels = state.basis_labels()
        st.latex(
            r"\begin{bmatrix} " + r" \\ ".join(rf"\langle {l}|\psi\rangle" for l in labels) + r" \end{bmatrix} = "
            + vector_latex(state.as_vector())
        )
        st.caption("Amplitudes are listed in the order " + ", ".join(f"|{l}⟩" for l in labels)
                   + " — qubit 0 is the leftmost bit.")
    recognised = recognise_state(state)
    if recognised is not None and recognised.has_phase:
        st.caption(
            f"This is {recognised.name_text} multiplied by the global phase "
            f"{recognised.text[: -len(recognised.name_text)]}. A global phase is physically "
            "unobservable: the probabilities and the Bloch arrow are identical to those of "
            f"{recognised.name_text}."
        )
