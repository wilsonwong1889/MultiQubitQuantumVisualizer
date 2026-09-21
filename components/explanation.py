"""Short gate-specific explanation beneath the maths (Phase 12 of the plan)."""
from __future__ import annotations

import streamlit as st

from data.gate_descriptions import GATE_DESCRIPTIONS
from quantum.bloch import bloch_vector, length
from quantum.circuit import Operation
from quantum.complex_number import Complex
from quantum.state import QuantumState
from utils.format_state import complex_text, coordinate_text, state_name_text


def _vec_text(state: QuantumState, qubit: int = 0) -> str:
    return "(" + ", ".join(coordinate_text(c) for c in bloch_vector(state, qubit)) + ")"


def render(before: QuantumState, op: Operation, after: QuantumState) -> None:
    gate = op.gate_object
    info = GATE_DESCRIPTIONS.get(gate.symbol)
    n = before.num_qubits
    st.markdown("**What happened**")
    where = "" if n == 1 else " to q" + ", q".join(str(t) for t in op.targets)
    summary = info.summary if info else gate.description
    st.markdown(
        f"Applying **{gate.symbol}**{where} took the system from **{state_name_text(before)}** "
        f"to **{state_name_text(after)}**. {summary}"
    )

    if n == 1:
        st.markdown(
            f"**On the Bloch sphere:** {info.bloch if info else ''} The arrow moved from {_vec_text(before)} "
            f"to {_vec_text(after)}."
        )
    else:
        pure_before = [before.is_pure_on(q) for q in range(n)]
        pure_after = [after.is_pure_on(q) for q in range(n)]
        if info and gate.arity == 1:
            q = op.targets[0]
            st.markdown(f"**On q{q}'s Bloch sphere:** {info.bloch} Its arrow moved from {_vec_text(before, q)} "
                        f"to {_vec_text(after, q)}; the other qubit(s) did not change.")
        elif info:
            st.markdown(f"**On the Bloch spheres:** {info.bloch}")
        newly_entangled = [q for q in range(n) if pure_before[q] and not pure_after[q]]
        newly_separable = [q for q in range(n) if not pure_before[q] and pure_after[q]]
        if newly_entangled:
            st.info(
                "The qubits are now **entangled**: q" + ", q".join(str(q) for q in newly_entangled)
                + " no longer has a definite state of its own, so its Bloch arrow shrinks toward the centre "
                  "(arrow length " + ", ".join(f"{length(bloch_vector(after, q)):.2f}" for q in newly_entangled)
                + "). Only the whole register has a state.",
                icon="🔗",
            )
        elif newly_separable:
            st.info("The qubits are separable again — each one has its own definite state and a full-length arrow.", icon="✂️")

    phase = after.global_phase_relative_to(before)
    if phase is not None:
        if phase.is_close(Complex(1.0, 0.0)):
            st.info(
                "The state did not change at all: it already lies on this gate's rotation axis, "
                "so rotating about that axis leaves it where it is." if n == 1 else
                "The state did not change: this gate acts trivially on the current state.",
                icon="📌",
            )
        else:
            st.info(
                f"Only a global phase changed (the whole state was multiplied by {complex_text(phase)}). "
                "A global phase has no physical effect, so the probabilities and the Bloch arrow are "
                "exactly the same as before — the maths differs, the physics does not.",
                icon="📌",
            )
    if info:
        st.caption(f"💡 {info.tip}")
