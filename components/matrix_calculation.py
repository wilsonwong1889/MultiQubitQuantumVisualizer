"""The matrix multiplication that maps the previous state to the current one (Phase 8)."""
from __future__ import annotations

import streamlit as st

from components.widgets import section
from quantum.circuit import Operation
from quantum.gates import Gate
from quantum.state import QuantumState, full_operator
from utils.format_state import (
    factor_latex,
    gate_symbol_latex,
    ket_latex,
    matrix_latex,
    state_chain_aligned,
    vector_latex,
)


def _single_qubit(before: QuantumState, gate: Gate, after: QuantumState, step: int) -> None:
    symbol = gate.symbol
    scale = gate.display_scale_latex
    shown = gate.shown_matrix
    v = before.as_vector()
    psi_before = rf"|\psi_{{{step - 1}}}\rangle"
    psi_after = rf"|\psi_{{{step}}}\rangle"

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


def _multi_qubit(before: QuantumState, op: Operation, after: QuantumState, step: int) -> None:
    gate = op.gate_object
    n = before.num_qubits
    psi_before = rf"|\psi_{{{step - 1}}}\rangle"
    psi_after = rf"|\psi_{{{step}}}\rangle"
    where = "q" + ", q".join(str(t) for t in op.targets)

    st.latex(rf"\text{{Before: }} {psi_before} = {ket_latex(before)}")
    st.markdown(f"**{gate.symbol}** acts on {where}" + (" (control first)" if gate.symbol in ("CNOT", "CZ") else "") + ":")
    sym = gate_symbol_latex(gate.symbol)
    st.latex(f"{sym} = {matrix_latex(gate.shown_matrix, gate.display_scale_latex)}")
    if n == 2:
        u = full_operator(gate, op.targets, n)
        st.markdown("On the whole two-qubit register this is the 4×4 operator "
                    + (r"$U = " + sym + r" \otimes I$" if gate.arity == 1 and op.targets == (0,) else
                       r"$U = I \otimes " + sym + "$" if gate.arity == 1 else "$U$") + ":")
        st.latex(
            r"\begin{aligned} U" + psi_before + " &= " + matrix_latex(u) + vector_latex(before.as_vector())
            + r" \\[6pt] &= " + vector_latex(after.as_vector()) + r" \end{aligned}"
        )
    else:
        st.latex(
            r"\begin{aligned} U" + psi_before + " &= " + vector_latex(after.as_vector()) + r" \end{aligned}"
        )
        st.caption("The full 8×8 operator is not shown; the gate acts on its target qubits and leaves the rest unchanged.")
    st.latex(state_chain_aligned(after, symbol=rf"\text{{After: }} {psi_after}"))


def render(before: QuantumState, op: Operation, after: QuantumState, step: int) -> None:
    gate = op.gate_object
    section("🔁", f"Transformation at step {step}: applying {gate.symbol}")
    if before.num_qubits == 1:
        _single_qubit(before, gate, after, step)
    else:
        _multi_qubit(before, op, after, step)
