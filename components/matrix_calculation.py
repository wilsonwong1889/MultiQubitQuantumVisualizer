"""The matrix multiplication that maps the previous state to the current one (Phase 8)."""
from __future__ import annotations

import streamlit as st

from quantum.gates import Gate
from quantum.qubit import QubitState
from utils.format_state import (
    factor_latex,
    ket_latex,
    matrix_latex,
    state_chain_aligned,
    vector_latex,
)


def render(before: QubitState, gate: Gate, after: QubitState, step: int) -> None:
    symbol = gate.symbol
    scale = gate.display_scale_latex
    shown = gate.shown_matrix
    v = before.as_vector()
    psi_before = rf"|\psi_{{{step - 1}}}\rangle"
    psi_after = rf"|\psi_{{{step}}}\rangle"

    st.markdown(f"**Transformation at step {step}: applying {symbol}**")
    st.latex(
        rf"\begin{{aligned}} \text{{Before: }} {psi_before} &= {ket_latex(before)}"
        rf" \\ &= {vector_latex(v)} \end{{aligned}}"
    )
    st.latex(f"{symbol} = {matrix_latex(shown, scale)}")

    # Row-by-row expansion of the product, using the "pretty" (unscaled) matrix.
    expanded_rows = [
        rf"{factor_latex(row[0])} \cdot {factor_latex(v[0])} + {factor_latex(row[1])} \cdot {factor_latex(v[1])}"
        for row in shown.rows
    ]
    expanded = r"\begin{bmatrix} %s \\ %s \end{bmatrix}" % tuple(expanded_rows)
    summed = vector_latex(shown.multiply_vector(v))
    result = vector_latex(after.as_vector())

    lines = [
        f"{symbol}{psi_before} &= {scale}{matrix_latex(shown)}{vector_latex(v)}",
        f"&= {scale}{expanded}",
    ]
    if scale:
        lines.append(f"&= {scale}{summed}")
    lines.append(f"&= {result}")
    st.latex(r"\begin{aligned} " + r" \\[6pt] ".join(lines) + r" \end{aligned}")
    st.latex(state_chain_aligned(after, symbol=rf"\text{{After: }} {psi_after}"))
