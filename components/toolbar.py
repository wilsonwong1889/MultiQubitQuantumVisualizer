"""Top card: number of qubits, initial states, gate palette and examples."""
from __future__ import annotations

import streamlit as st

import model
from components.widgets import choose, section
from data.presets import PRESETS, PRESETS_BY_KEY
from quantum.gates import GATES, SINGLE_QUBIT_GATES, TWO_QUBIT_GATES
from quantum.state import INITIAL_STATE_LABELS, INITIAL_STATES


def render() -> None:
    s = st.session_state
    n = s.num_qubits
    with st.container(border=True):
        c_setup, c_gates = st.columns([1, 1.6], gap="large")

        with c_setup:
            section("🧭", "Set up the register")
            choose("Number of qubits", model.QUBIT_OPTIONS, key="qubit_count",
                   default=n, on_change=model.set_num_qubits,
                   help="Changing the number of qubits clears the circuit.")
            for q in range(n):
                choose(f"q{q} starts in", list(INITIAL_STATES), key=f"init_{q}",
                       format_func=lambda key: INITIAL_STATE_LABELS[key],
                       on_change=model.on_initial_state_change)

        with c_gates:
            section("🎛️", "Add gates", "Each click appends a gate to the end of the circuit.")
            full = len(s.ops) >= model.MAX_OPERATIONS
            if n > 1:
                choose("Apply single-qubit gates to", list(range(n)), key="target",
                       format_func=lambda q: f"q{q}")
            cols = st.columns(len(SINGLE_QUBIT_GATES))
            for col, symbol in zip(cols, SINGLE_QUBIT_GATES):
                with col:
                    st.button(symbol, key=f"add_{symbol}", on_click=model.add_single_qubit_gate,
                              args=(symbol,), help=GATES[symbol].description, disabled=full, width="stretch")
            if n > 1:
                c_ctrl, c_tgt = st.columns(2)
                with c_ctrl:
                    choose("Control", list(range(n)), key="ctrl", format_func=lambda q: f"q{q}", default=0)
                with c_tgt:
                    choose("Target", list(range(n)), key="tgt", format_func=lambda q: f"q{q}", default=1)
                same = s.get("ctrl") == s.get("tgt")
                cols = st.columns(len(TWO_QUBIT_GATES) + (len(SINGLE_QUBIT_GATES) - len(TWO_QUBIT_GATES)))
                for col, symbol in zip(cols, TWO_QUBIT_GATES):
                    with col:
                        st.button(symbol, key=f"add_{symbol}", on_click=model.add_two_qubit_gate,
                                  args=(symbol,), help=GATES[symbol].description,
                                  disabled=full or same, width="stretch")
                if same:
                    st.caption("Pick two different qubits for a two-qubit gate.")
            if full:
                st.caption(f"Maximum of {model.MAX_OPERATIONS} gates reached.")

        st.selectbox(
            "Load an example", options=[p.key for p in PRESETS],
            format_func=lambda key: PRESETS_BY_KEY[key].label,
            index=None, placeholder="Load an example circuit…", key="preset_select",
            on_change=model.load_selected_preset, width=360,
        )
