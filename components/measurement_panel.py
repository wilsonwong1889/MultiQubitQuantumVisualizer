"""Measurement probabilities and a sampling experiment (Phase 7 + Version 2 measurements)."""
from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

import model
from components.theme import SERIES_OBSERVED, SERIES_THEORY
from components.widgets import choose, section
from quantum.state import QuantumState
from utils.format_state import real_latex, state_chain_latex


def _clamp(p: float) -> float:
    return min(1.0, max(0.0, p))


def _histogram(labels, theory, observed, shots: int) -> go.Figure:
    fig = go.Figure()
    fig.add_bar(name="Theory", x=[f"|{l}⟩" for l in labels], y=theory, marker_color=SERIES_THEORY,
                marker=dict(cornerradius=4), text=[f"{v:.0f}%" for v in theory], textposition="outside",
                hovertemplate="%{x}: %{y:.1f}% expected<extra>Theory</extra>")
    fig.add_bar(name=f"Observed ({shots} shots)", x=[f"|{l}⟩" for l in labels], y=observed,
                marker_color=SERIES_OBSERVED, marker=dict(cornerradius=4),
                text=[f"{v:.0f}%" for v in observed], textposition="outside",
                hovertemplate="%{x}: %{y:.1f}% observed<extra>Observed</extra>")
    fig.update_layout(
        barmode="group", bargap=0.3, bargroupgap=0.08, height=280,
        margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0), font=dict(color="#475569"),
        yaxis=dict(title="% of shots", range=[0, 112], gridcolor="#E5E7EB", zeroline=False, ticksuffix="%"),
        xaxis=dict(showgrid=False),
    )
    return fig


def render(state: QuantumState) -> None:
    n = state.num_qubits
    labels = state.basis_labels()
    probs = [_clamp(p) for p in state.probabilities()]
    section("🎯", "Measurement", "Probabilities of each outcome when the register is measured in the computational basis.")

    if n == 1:
        p0, p1 = probs
        st.latex(
            r"\begin{aligned} P(0) &= |\alpha|^2 = " + real_latex(p0) + rf" = {p0 * 100:.0f}\%"
            + r" \\ P(1) &= |\beta|^2 = " + real_latex(p1) + rf" = {p1 * 100:.0f}\%"
            + r" \end{aligned}"
        )
    else:
        st.latex(r"P(k) = |\langle k|\psi\rangle|^2")
    bar_columns = st.columns(2) if len(labels) > 4 else [st.container()]
    for i, (label, p) in enumerate(zip(labels, probs)):
        with bar_columns[i % len(bar_columns)]:
            st.progress(p, text=f"|{label}⟩ — {p * 100:.1f}%")
    st.caption(
        "Why squared? An amplitude can be negative or imaginary, but a probability cannot. "
        "|a|² = a*·a is always a non-negative real number, and the squares add up to 1."
    )
    if n == 1 and abs(probs[0] - 0.5) < 1e-9:
        st.info(
            "50/50 — but which 50/50? |+⟩, |−⟩, |+i⟩ and |−i⟩ all give exactly these probabilities, "
            "yet they are different states. The Bloch sphere shows the difference: they point in "
            "four different directions around the equator.",
            icon="🎯",
        )

    st.markdown("**Try it: run the experiment**")
    c_shots, c_button = st.columns([2, 1], vertical_alignment="bottom")
    with c_shots:
        choose("Shots", model.SHOT_OPTIONS, key="shots", default=100, format_func=lambda k: f"{k:,}")
    with c_button:
        st.button("🎲 Measure", key="measure_button", on_click=model.run_measurement, width="stretch")

    result = st.session_state.get("measurement")
    if not result or result["signature"] != model.signature():
        st.caption("Measurement destroys the superposition: one shot gives a single outcome, "
                   "many shots reveal the probabilities.")
        return
    if result["shots"] == 1:
        outcome = result["outcome"]
        st.success(f"Outcome: |{outcome}⟩ — the register collapsed to that basis state.", icon="📏")
        st.latex(state_chain_latex(result["collapsed"], symbol=r"|\psi_{\text{after}}\rangle"))
    else:
        counts = result["counts"]
        shots_run = result["shots"]
        observed = [100.0 * counts[l] / shots_run for l in labels]
        theory = [100.0 * p for p in probs]
        st.plotly_chart(_histogram(labels, theory, observed, shots_run), width="stretch",
                        config={"displayModeBar": False}, key="measurement_histogram")
        st.caption("Observed: " + ", ".join(f"|{l}⟩ × {counts[l]}" for l in labels if counts[l])
                   + ". More shots bring the observed frequencies closer to the theoretical probabilities.")
