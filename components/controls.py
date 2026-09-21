"""Previous / Next / Undo / Reset controls (Phase 6 of the plan)."""
from __future__ import annotations

from typing import Callable

import streamlit as st


def render(current_step: int, total_steps: int,
           on_previous: Callable[[], None], on_next: Callable[[], None],
           on_undo: Callable[[], None], on_reset: Callable[[], None]) -> None:
    c_prev, c_label, c_next, c_spacer, c_undo, c_reset = st.columns(
        [1.1, 1.2, 1.1, 0.6, 1, 1], vertical_alignment="center"
    )
    with c_prev:
        st.button("◀ Previous", disabled=current_step == 0, on_click=on_previous, width="stretch")
    with c_label:
        st.markdown(
            f"<div style='text-align:center;font-weight:600;'>Step {current_step} / {total_steps}</div>",
            unsafe_allow_html=True,
        )
    with c_next:
        st.button("Next ▶", disabled=current_step >= total_steps, on_click=on_next, width="stretch")
    with c_undo:
        st.button("↶ Undo gate", disabled=total_steps == 0, on_click=on_undo, width="stretch",
                  help="Remove the most recent gate")
    with c_reset:
        st.button("Reset", disabled=total_steps == 0 and current_step == 0, on_click=on_reset,
                  width="stretch", help="Clear the circuit and return to the initial state")
