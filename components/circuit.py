"""One horizontal qubit wire with clickable gate nodes (Phases 5-6 of the plan)."""
from __future__ import annotations

from typing import Callable, List

import streamlit as st

WIRE_HTML = (
    '<div style="height:2.5rem;display:flex;align-items:center;">'
    '<div style="width:100%;height:2px;background:#8a94a6;"></div></div>'
)


def render(initial_label: str, gate_symbols: List[str], current_step: int,
           on_select: Callable[[int], None]) -> None:
    n = len(gate_symbols)
    st.markdown("**Quantum circuit** — click any node to inspect that point in the circuit")

    # initial-state node, then (wire, gate) pairs, then a trailing wire.
    weights = [1.3] + [0.6, 1.0] * n + [0.6]
    cols = st.columns(weights, vertical_alignment="center")

    with cols[0]:
        st.button(
            initial_label, key="circuit_node_0",
            type="primary" if current_step == 0 else "secondary",
            on_click=on_select, args=(0,),
            help="Step 0: the initial state, before any gate", width="stretch",
        )
    for i, symbol in enumerate(gate_symbols, start=1):
        with cols[2 * i - 1]:
            st.markdown(WIRE_HTML, unsafe_allow_html=True)
        with cols[2 * i]:
            st.button(
                symbol, key=f"circuit_node_{i}",
                type="primary" if current_step == i else "secondary",
                on_click=on_select, args=(i,),
                help=f"Step {i}: apply {symbol}", width="stretch",
            )
    with cols[-1]:
        st.markdown(WIRE_HTML, unsafe_allow_html=True)

    # marker row under the highlighted node
    marker_cols = st.columns(weights)
    with marker_cols[2 * current_step]:
        st.caption("▲ initial state" if current_step == 0 else "▲ current gate")
