"""Short gate-specific explanation beneath the maths (Phase 12 of the plan)."""
from __future__ import annotations

import streamlit as st

from data.gate_descriptions import GATE_DESCRIPTIONS
from quantum.bloch import bloch_vector
from quantum.gates import Gate
from quantum.qubit import QubitState
from utils.format_state import complex_text, coordinate_text, state_name_text


def _vec_text(state: QubitState) -> str:
    return "(" + ", ".join(coordinate_text(c) for c in bloch_vector(state)) + ")"


def render(before: QubitState, gate: Gate, after: QubitState) -> None:
    info = GATE_DESCRIPTIONS[gate.symbol]
    st.markdown("**What happened**")
    st.markdown(
        f"Applying **{gate.symbol}** took the qubit from **{state_name_text(before)}** "
        f"to **{state_name_text(after)}**. {info.summary}"
    )
    st.markdown(
        f"**On the Bloch sphere:** {info.bloch} The arrow moved from {_vec_text(before)} "
        f"to {_vec_text(after)}."
    )
    phase = after.global_phase_relative_to(before)
    if phase is not None:
        if phase.is_close(type(phase)(1.0, 0.0)):
            st.info(
                "The state did not change at all: it already lies on this gate's rotation axis, "
                "so rotating about that axis leaves it where it is.",
                icon="📌",
            )
        else:
            st.info(
                f"Only a global phase changed (the whole state was multiplied by {complex_text(phase)}). "
                "A global phase has no physical effect, so the probabilities and the Bloch arrow are "
                "exactly the same as before — the maths differs, the physics does not.",
                icon="📌",
            )
    st.caption(f"💡 {info.tip}")
