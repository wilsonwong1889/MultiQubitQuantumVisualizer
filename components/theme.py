"""Custom CSS: coloured gate buttons, tidy formulas, compact spacing."""
from __future__ import annotations

import streamlit as st

from quantum.gates import GATES

ACCENT = "#6C5CE7"
WIRE = "#94A3B8"
INK = "#334155"
MUTED = "#64748B"
SERIES_THEORY = "#2A78D6"
SERIES_OBSERVED = "#EB6834"


def _gate_button_css(key: str, color: str) -> str:
    return (
        f".st-key-{key} button {{ background:{color}; color:#fff !important; border:1px solid {color};"
        f" font-weight:700; letter-spacing:.02em; }}"
        f".st-key-{key} button:hover {{ filter:brightness(1.07); border-color:{color}; color:#fff !important; }}"
        f".st-key-{key} button:active {{ filter:brightness(.95); }}"
        f".st-key-{key} button:disabled {{ opacity:.35; }}"
    )


def inject() -> None:
    rules = [
        ".katex-display { overflow-x: auto; overflow-y: hidden; padding: 2px 0; }",
        ".block-container { padding-top: 1.6rem; }",
        "h4 { margin-bottom: 0.2rem !important; }",
        f".st-key-measure_button button {{ background:{ACCENT}; color:#fff !important; border-color:{ACCENT}; font-weight:700; }}",
        f".st-key-measure_button button:hover {{ filter:brightness(1.07); color:#fff !important; border-color:{ACCENT}; }}",
    ]
    rules += [_gate_button_css(f"add_{symbol}", gate.color) for symbol, gate in GATES.items()]
    st.markdown("<style>" + "\n".join(rules) + "</style>", unsafe_allow_html=True)
