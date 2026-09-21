"""Interactive 3D Bloch spheres built with Plotly (Phases 9-11 of the plan).

One sphere is drawn per qubit. The sphere, axes and labels are static
decoration; the state arrow is the last two traces (a line and a cone) so the
animation frames only need to replace those, sweeping the arrow along the
gate's rotation path (or straight through the ball when a qubit becomes
entangled and its arrow shrinks).
"""
from __future__ import annotations

from typing import List, Optional

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from components.widgets import section
from quantum.bloch import Vec3, bloch_vector, length, rotation_path, straight_path
from quantum.circuit import Operation
from quantum.state import QuantumState
from utils.format_state import coordinate_text

ARROW_COLOR = "#E4572E"
GHOST_COLOR = "#94A3B8"
SPHERE_COLOR = "#6C8EF5"
WIRE_COLOR = "#C7CEDB"
AXIS_COLOR = "#8A94A6"
TEXT_COLOR = "#475569"
GATE_AXIS_COLOR = "#8E44AD"

ANIMATION_STEPS = 36
FRAME_MS = 30
AXIS_RANGE = 1.4


def _sphere() -> go.Surface:
    u = np.linspace(0, 2 * np.pi, 60)
    v = np.linspace(0, np.pi, 30)
    x = np.outer(np.cos(u), np.sin(v))
    y = np.outer(np.sin(u), np.sin(v))
    z = np.outer(np.ones_like(u), np.cos(v))
    return go.Surface(
        x=x, y=y, z=z,
        opacity=0.10,
        colorscale=[[0, SPHERE_COLOR], [1, SPHERE_COLOR]],
        showscale=False,
        hoverinfo="skip",
        lighting=dict(ambient=0.9, diffuse=0.4, specular=0.05),
    )


def _great_circles() -> List[go.Scatter3d]:
    t = np.linspace(0, 2 * np.pi, 120)
    zeros = np.zeros_like(t)
    circles = [
        (np.cos(t), np.sin(t), zeros),   # equator (xy-plane)
        (np.cos(t), zeros, np.sin(t)),   # xz-plane meridian
        (zeros, np.cos(t), np.sin(t)),   # yz-plane meridian
    ]
    return [
        go.Scatter3d(x=x, y=y, z=z, mode="lines",
                     line=dict(color=WIRE_COLOR, width=1.5), hoverinfo="skip")
        for x, y, z in circles
    ]


def _axes() -> List[go.BaseTraceType]:
    traces: List[go.BaseTraceType] = []
    for unit, label in (((1, 0, 0), "x"), ((0, 1, 0), "y"), ((0, 0, 1), "z")):
        traces.append(go.Scatter3d(
            x=[-1.3 * unit[0], 1.3 * unit[0]],
            y=[-1.3 * unit[1], 1.3 * unit[1]],
            z=[-1.3 * unit[2], 1.3 * unit[2]],
            mode="lines", line=dict(color=AXIS_COLOR, width=2), hoverinfo="skip",
        ))
        traces.append(go.Scatter3d(
            x=[1.4 * unit[0]], y=[1.4 * unit[1]], z=[1.4 * unit[2]],
            mode="text", text=[label], textfont=dict(color=TEXT_COLOR, size=13),
            hoverinfo="skip",
        ))
    return traces


def _basis_labels() -> go.Scatter3d:
    points = [
        ((0, 0, 1.13), "|0⟩"),
        ((0, 0, -1.16), "|1⟩"),
        ((1.16, 0, 0), "|+⟩"),
        ((-1.18, 0, 0), "|−⟩"),
        ((0, 1.16, 0), "|+i⟩"),
        ((0, -1.18, 0), "|−i⟩"),
    ]
    return go.Scatter3d(
        x=[p[0][0] for p in points], y=[p[0][1] for p in points], z=[p[0][2] for p in points],
        mode="text", text=[p[1] for p in points],
        textfont=dict(color=TEXT_COLOR, size=16), hoverinfo="skip",
    )


def _arrow(vec: Vec3, color: str, width: float, cone_size: float, dash: Optional[str] = None,
           label: str = "state") -> List[go.BaseTraceType]:
    line = go.Scatter3d(
        x=[0, vec[0]], y=[0, vec[1]], z=[0, vec[2]],
        mode="lines", line=dict(color=color, width=width, dash=dash) if dash else dict(color=color, width=width),
        hovertemplate=f"{label}<br>x = %{{x:.3f}}<br>y = %{{y:.3f}}<br>z = %{{z:.3f}}<extra></extra>",
    )
    if length(vec) < 1e-6:
        # No direction to point in: mark the centre instead of drawing a cone.
        cone = go.Scatter3d(x=[0], y=[0], z=[0], mode="markers",
                            marker=dict(color=color, size=7), hoverinfo="skip")
    else:
        cone = go.Cone(
            x=[vec[0]], y=[vec[1]], z=[vec[2]],
            u=[vec[0]], v=[vec[1]], w=[vec[2]],
            anchor="tip", sizemode="absolute", sizeref=cone_size * max(length(vec), 0.35),
            colorscale=[[0, color], [1, color]], showscale=False, hoverinfo="skip",
        )
    return [line, cone]


def _gate_axis(axis: Vec3, symbol: str) -> go.Scatter3d:
    return go.Scatter3d(
        x=[-1.25 * axis[0], 1.25 * axis[0]], y=[-1.25 * axis[1], 1.25 * axis[1]], z=[-1.25 * axis[2], 1.25 * axis[2]],
        mode="lines", line=dict(color=GATE_AXIS_COLOR, width=3, dash="dash"),
        hovertemplate=f"rotation axis of {symbol}<extra></extra>",
    )


def arrow_path(previous: Optional[QuantumState], current: QuantumState, op: Optional[Operation], qubit: int) -> List[Vec3]:
    """How this qubit's arrow travels during the current operation."""
    if previous is None or op is None:
        return []
    start, end = bloch_vector(previous, qubit), bloch_vector(current, qubit)
    gate = op.gate_object
    if gate.arity == 1 and op.targets == (qubit,) and gate.is_rotation and previous.is_pure_on(qubit):
        return rotation_path(start, gate.axis, gate.rotation, ANIMATION_STEPS)
    if length(tuple(e - s for s, e in zip(start, end))) < 1e-9:
        return []
    return straight_path(start, end, ANIMATION_STEPS)


def build_figure(current: QuantumState, previous: Optional[QuantumState], op: Optional[Operation],
                 qubit: int = 0, height: int = 540) -> go.Figure:
    current_vec = bloch_vector(current, qubit)
    traces: List[go.BaseTraceType] = [_sphere(), *_great_circles(), *_axes(), _basis_labels()]

    path = arrow_path(previous, current, op, qubit)
    if previous is not None and op is not None:
        gate = op.gate_object
        if gate.arity == 1 and op.targets == (qubit,) and gate.is_rotation:
            traces.append(_gate_axis(gate.axis, gate.symbol))
        traces += _arrow(bloch_vector(previous, qubit), GHOST_COLOR, 5, 0.16, dash="dash", label="previous state")
        if path:
            traces.append(go.Scatter3d(
                x=[p[0] for p in path], y=[p[1] for p in path], z=[p[2] for p in path],
                mode="lines", line=dict(color=ARROW_COLOR, width=3, dash="dot"), hoverinfo="skip",
            ))

    arrow_index = len(traces)
    traces += _arrow(current_vec, ARROW_COLOR, 9, 0.22, label="current state")
    fig = go.Figure(data=traces)

    if path:
        fig.frames = [
            go.Frame(
                data=_arrow(point, ARROW_COLOR, 9, 0.22, label="current state"),
                traces=[arrow_index, arrow_index + 1],
                name=str(k),
            )
            for k, point in enumerate(path)
        ]
        fig.update_layout(updatemenus=[dict(
            type="buttons", showactive=False,
            x=0.0, y=1.0, xanchor="left", yanchor="top", pad=dict(l=6, t=6),
            bgcolor="rgba(255,255,255,0.9)", bordercolor=ARROW_COLOR,
            font=dict(color=ARROW_COLOR, size=13),
            buttons=[dict(
                label=f"▶ Animate {op.gate}",
                method="animate",
                args=[None, dict(frame=dict(duration=FRAME_MS, redraw=True),
                                 transition=dict(duration=0), fromcurrent=False, mode="immediate")],
            )],
        )])

    hidden_axis = dict(visible=False, range=[-AXIS_RANGE, AXIS_RANGE])
    fig.update_layout(
        scene=dict(
            xaxis=hidden_axis, yaxis=hidden_axis, zaxis=hidden_axis,
            aspectmode="cube",
            camera=dict(eye=dict(x=1.05, y=0.9, z=0.55), up=dict(x=0, y=0, z=1)),
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=height,
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        uirevision=f"bloch-{qubit}",  # keep the camera where the student left it between reruns
    )
    return fig


def _coords_latex(state: QuantumState, qubit: int) -> str:
    return "(%s,\\ %s,\\ %s)" % tuple(coordinate_text(c) for c in bloch_vector(state, qubit))


def render(current: QuantumState, previous: Optional[QuantumState], op: Optional[Operation]) -> None:
    n = current.num_qubits
    section("🌐", "Bloch sphere" if n == 1 else "Bloch spheres — one per qubit")
    hint = "Drag to rotate · scroll to zoom"
    if op is not None:
        hint += (f" · press ▶ to replay {op.gate}. Grey arrow = previous state, dotted line = path of the arrow"
                 + (", purple dashed line = rotation axis." if op.gate_object.is_rotation else "."))
    st.caption(hint)

    height = {1: 540, 2: 400}.get(n, 330)
    columns = st.columns(n) if n > 1 else [st.container()]
    for qubit, col in enumerate(columns):
        with col:
            if n > 1:
                st.markdown(f"**q{qubit}**")
            fig = build_figure(current, previous, op, qubit=qubit, height=height)
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False, "scrollZoom": True},
                            key=f"bloch_{qubit}")
            radius = length(bloch_vector(current, qubit))
            line = r"(x,\ y,\ z) = " + _coords_latex(current, qubit)
            if previous is not None:
                line = (r"\begin{aligned} (x,\ y,\ z) &= " + _coords_latex(current, qubit)
                        + r" \\ \text{previous} &= " + _coords_latex(previous, qubit) + r" \end{aligned}")
            st.latex(line)
            if n > 1:
                if radius > 1 - 1e-6:
                    st.caption(f"Arrow length {radius:.2f}: this qubit has a definite state of its own.")
                else:
                    st.caption(f"Arrow length {radius:.2f}: this qubit is entangled with the other(s) — "
                               "its reduced state is mixed.")
    if n == 1:
        st.latex(
            r"\begin{gathered} x = 2\,\mathrm{Re}(\alpha^{*}\beta), \quad "
            r"y = 2\,\mathrm{Im}(\alpha^{*}\beta) \\ z = |\alpha|^2 - |\beta|^2 \end{gathered}"
        )
