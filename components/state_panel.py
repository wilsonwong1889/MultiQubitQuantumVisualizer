"""Ket notation, vector notation and amplitudes (Phase 8 of the plan)."""
from __future__ import annotations

import streamlit as st

from quantum.qubit import QubitState
from utils.format_state import complex_latex, recognise_state, state_chain_aligned, vector_latex


def render(state: QubitState, step: int) -> None:
    st.markdown(f"**State after step {step}**" if step else "**Initial state**")
    st.latex(state_chain_aligned(state, symbol=rf"|\psi_{{{step}}}\rangle"))
    st.latex(
        r"\begin{gathered} \begin{bmatrix} \alpha \\ \beta \end{bmatrix} = " + vector_latex(state.as_vector())
        + r" \\[4pt] \alpha = " + complex_latex(state.alpha)
        + r", \qquad \beta = " + complex_latex(state.beta)
        + r" \end{gathered}"
    )
    recognised = recognise_state(state)
    if recognised is not None and recognised.has_phase:
        st.caption(
            f"This is {recognised.name_text} multiplied by the global phase "
            f"{recognised.text[: -len(recognised.name_text)]}. A global phase is physically "
            "unobservable: the probabilities and the Bloch arrow are identical to those of "
            f"{recognised.name_text}."
        )
