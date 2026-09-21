"""Measurement probabilities with bars (Phase 7 of the plan)."""
from __future__ import annotations

import streamlit as st

from quantum.qubit import QubitState
from utils.format_state import real_latex


def _clamp(p: float) -> float:
    return min(1.0, max(0.0, p))


def render(state: QubitState) -> None:
    p0, p1 = (_clamp(p) for p in state.probabilities())
    st.markdown("**Measurement probabilities**")
    st.latex(
        r"\begin{aligned} P(0) &= |\alpha|^2 = " + real_latex(p0) + rf" = {p0 * 100:.0f}\%"
        + r" \\ P(1) &= |\beta|^2 = " + real_latex(p1) + rf" = {p1 * 100:.0f}\%"
        + r" \end{aligned}"
    )
    st.progress(p0, text=f"|0⟩ — {p0 * 100:.1f}%")
    st.progress(p1, text=f"|1⟩ — {p1 * 100:.1f}%")
    st.caption(
        "Why squared? An amplitude can be negative or imaginary, but a probability cannot. "
        "|α|² = α*·α is always a non-negative real number, and |α|² + |β|² = 1 guarantees the "
        "two outcomes add up to 100%."
    )
    if abs(p0 - 0.5) < 1e-9:
        st.info(
            "50/50 — but which 50/50? |+⟩, |−⟩, |+i⟩ and |−i⟩ all give exactly these probabilities, "
            "yet they are different states. The Bloch sphere shows the difference: they point in "
            "four different directions around the equator.",
            icon="🎯",
        )
