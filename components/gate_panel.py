"""Gate matrix, description and basis-state actions (Section 9 of the plan)."""
from __future__ import annotations

from typing import Optional

import streamlit as st

from data.gate_descriptions import GATE_DESCRIPTIONS
from quantum.gates import GATE_ORDER, GATES, Gate
from utils.format_state import matrix_latex


def _gate_matrix_latex(gate: Gate) -> str:
    return matrix_latex(gate.shown_matrix, gate.display_scale_latex)


def render(gate: Optional[Gate]) -> None:
    if gate is not None:
        info = GATE_DESCRIPTIONS[gate.symbol]
        st.markdown(f"**About the {info.title}**")
        c_matrix, c_text = st.columns([1, 1.5], vertical_alignment="center")
        with c_matrix:
            st.latex(f"{gate.symbol} = {_gate_matrix_latex(gate)}")
        with c_text:
            st.markdown(info.summary)
        st.markdown("Action on common states:")
        st.latex(r" \qquad ".join(info.basis_actions[:2]))
        st.latex(r" \qquad ".join(info.basis_actions[2:]))

    with st.expander("All gates at a glance"):
        rows = ["| Gate | Matrix | Action | On the Bloch sphere |", "|---|---|---|---|"]
        for symbol in GATE_ORDER:
            g = GATES[symbol]
            d = GATE_DESCRIPTIONS[symbol]
            rows.append(f"| **{symbol}** — {g.name} | ${_gate_matrix_latex(g)}$ | {g.description} | {d.bloch} |")
        st.markdown("\n".join(rows))
