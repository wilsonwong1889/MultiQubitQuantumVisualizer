"""Previous / Next / Undo / Reset controls (Phase 6 of the plan)."""
from __future__ import annotations

import streamlit as st

import model


def render(current_step: int, total_steps: int) -> None:
    c_prev, c_label, c_next, c_spacer, c_undo, c_reset = st.columns(
        [1.1, 1.2, 1.1, 0.6, 1, 1], vertical_alignment="center"
    )
    with c_prev:
        st.button("◀ Previous", disabled=current_step == 0, on_click=model.previous_step, width="stretch")
    with c_label:
        st.markdown(
            f"<div style='text-align:center;font-weight:600;'>Step {current_step} / {total_steps}</div>",
            unsafe_allow_html=True,
        )
    with c_next:
        st.button("Next ▶", disabled=current_step >= total_steps, on_click=model.next_step, width="stretch")
    with c_undo:
        st.button("↶ Undo gate", disabled=total_steps == 0, on_click=model.undo_operation, width="stretch",
                  help="Remove the most recent gate")
    with c_reset:
        st.button("Reset", disabled=total_steps == 0 and current_step == 0, on_click=model.reset_circuit,
                  width="stretch", help="Clear the circuit and return to the initial state")
