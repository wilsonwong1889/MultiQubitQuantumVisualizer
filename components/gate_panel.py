"""Gate matrix, description and basis-state actions (Section 9 of the plan)."""
from __future__ import annotations

from typing import Optional

import streamlit as st

from components.widgets import section
from data.gate_descriptions import GATE_DESCRIPTIONS
from quantum.gates import GATES, SINGLE_QUBIT_GATES, TWO_QUBIT_GATES, Gate
from utils.format_state import gate_symbol_latex, matrix_latex


def _gate_matrix_latex(gate: Gate) -> str:
    return matrix_latex(gate.shown_matrix, gate.display_scale_latex)


def render(gate: Optional[Gate]) -> None:
    section("📖", "Gate reference")
    if gate is not None:
        info = GATE_DESCRIPTIONS[gate.symbol]
        st.markdown(f"**{info.title}**")
        c_matrix, c_text = st.columns([1, 1.5], vertical_alignment="center")
        with c_matrix:
            st.latex(f"{gate_symbol_latex(gate.symbol)} = {_gate_matrix_latex(gate)}")
        with c_text:
            st.markdown(info.summary)
        st.markdown("Action on common states:")
        st.latex(r" \qquad ".join(info.basis_actions[:2]))
        st.latex(r" \qquad ".join(info.basis_actions[2:]))
    else:
        st.caption("Add a gate or step forward to see details about the gate being applied.")

    with st.expander("All gates at a glance"):
        for title, symbols in (("Single-qubit gates", SINGLE_QUBIT_GATES), ("Two-qubit gates", TWO_QUBIT_GATES)):
            st.markdown(f"**{title}**")
            rows = ["| Gate | Matrix | Action | On the Bloch sphere |", "|---|---|---|---|"]
            for symbol in symbols:
                g = GATES[symbol]
                d = GATE_DESCRIPTIONS[symbol]
                rows.append(f"| **{symbol}** — {g.name} | ${_gate_matrix_latex(g)}$ | {g.description} | {d.bloch} |")
            st.markdown("\n".join(rows))
