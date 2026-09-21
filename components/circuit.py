"""The circuit diagram: one wire per qubit, drawn as SVG, plus a step timeline."""
from __future__ import annotations

from typing import List, Optional

import streamlit as st

import model
from components.theme import ACCENT, INK, MUTED, WIRE
from components.widgets import choose
from quantum.circuit import Circuit, Operation
from quantum.gates import get_gate
from quantum.state import INITIAL_STATE_LABELS

LABEL_W = 96      # room for "q0  |0⟩"
STEP_W = 92
ROW_H = 76
BOX = 46
FONT = "ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif"


def _wire_y(q: int) -> int:
    return ROW_H // 2 + ROW_H * q


def _single_gate(cx: int, cy: int, symbol: str, color: str, opacity: float) -> str:
    half = BOX // 2
    font_size = 18 if len(symbol) == 1 else 12
    return (
        f'<g opacity="{opacity}">'
        f'<rect x="{cx - half}" y="{cy - half}" width="{BOX}" height="{BOX}" rx="10" fill="{color}"/>'
        f'<text x="{cx}" y="{cy + 1}" text-anchor="middle" dominant-baseline="middle" '
        f'font-family="{FONT}" font-size="{font_size}" font-weight="700" fill="#fff">{symbol}</text></g>'
    )


def _two_qubit_gate(cx: int, op: Operation, color: str, opacity: float) -> str:
    a, b = op.targets
    ya, yb = _wire_y(a), _wire_y(b)
    parts = [f'<g opacity="{opacity}"><line x1="{cx}" y1="{ya}" x2="{cx}" y2="{yb}" stroke="{color}" stroke-width="3"/>']
    if op.gate == "CNOT":
        parts.append(f'<circle cx="{cx}" cy="{ya}" r="7" fill="{color}"/>')
        parts.append(f'<circle cx="{cx}" cy="{yb}" r="14" fill="#fff" stroke="{color}" stroke-width="3"/>')
        parts.append(f'<line x1="{cx - 9}" y1="{yb}" x2="{cx + 9}" y2="{yb}" stroke="{color}" stroke-width="3"/>')
        parts.append(f'<line x1="{cx}" y1="{yb - 9}" x2="{cx}" y2="{yb + 9}" stroke="{color}" stroke-width="3"/>')
    elif op.gate == "CZ":
        parts.append(f'<circle cx="{cx}" cy="{ya}" r="7" fill="{color}"/>')
        parts.append(f'<circle cx="{cx}" cy="{yb}" r="7" fill="{color}"/>')
    else:  # SWAP and any future symmetric gate: an X on each wire
        for y in (ya, yb):
            parts.append(f'<line x1="{cx - 8}" y1="{y - 8}" x2="{cx + 8}" y2="{y + 8}" stroke="{color}" stroke-width="3"/>')
            parts.append(f'<line x1="{cx - 8}" y1="{y + 8}" x2="{cx + 8}" y2="{y - 8}" stroke="{color}" stroke-width="3"/>')
        if op.gate != "SWAP":
            parts.append(f'<text x="{cx}" y="{min(ya, yb) - 18}" text-anchor="middle" font-family="{FONT}" '
                         f'font-size="11" font-weight="700" fill="{color}">{op.gate}</text>')
    parts.append("</g>")
    return "".join(parts)


def circuit_svg(circuit: Circuit, current_step: int) -> str:
    n = circuit.num_qubits
    ops = circuit.operations
    columns = max(len(ops), 1)
    width = LABEL_W + STEP_W * columns + 36 + (150 if not ops else 0)   # room for the placeholder hint
    height = ROW_H * n + 22
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
             f'viewBox="0 0 {width} {height}" style="display:block;max-width:100%;height:auto">']

    # current-step highlight behind everything
    if current_step > 0:
        cx = LABEL_W + STEP_W * (current_step - 1) + STEP_W // 2
        parts.append(f'<rect x="{cx - STEP_W // 2 + 6}" y="6" width="{STEP_W - 12}" height="{ROW_H * n - 12}" '
                     f'rx="14" fill="{ACCENT}" fill-opacity="0.10" stroke="{ACCENT}" stroke-width="2" stroke-dasharray="6 4"/>')
        parts.append(f'<text x="{cx}" y="{ROW_H * n + 12}" text-anchor="middle" font-family="{FONT}" '
                     f'font-size="11" font-weight="600" fill="{ACCENT}">▲ step {current_step}</text>')
    else:
        parts.append(f'<rect x="10" y="6" width="{LABEL_W - 22}" height="{ROW_H * n - 12}" rx="14" '
                     f'fill="{ACCENT}" fill-opacity="0.08" stroke="{ACCENT}" stroke-width="2" stroke-dasharray="6 4"/>')
        parts.append(f'<text x="{LABEL_W // 2 - 1}" y="{ROW_H * n + 12}" text-anchor="middle" font-family="{FONT}" '
                     f'font-size="11" font-weight="600" fill="{ACCENT}">▲ start</text>')

    # wires and labels
    for q in range(n):
        y = _wire_y(q)
        parts.append(f'<line x1="{LABEL_W - 8}" y1="{y}" x2="{width - 12}" y2="{y}" stroke="{WIRE}" stroke-width="2"/>')
        parts.append(f'<text x="{LABEL_W - 16}" y="{y + 1}" text-anchor="end" dominant-baseline="middle" '
                     f'font-family="{FONT}" font-size="15" fill="{INK}"><tspan fill="{MUTED}" font-size="12">q{q}</tspan>'
                     f'  {INITIAL_STATE_LABELS[circuit.initial[q]]}</text>')

    # gates
    for i, op in enumerate(ops, start=1):
        gate = get_gate(op.gate)
        cx = LABEL_W + STEP_W * (i - 1) + STEP_W // 2
        opacity = 1.0 if i <= current_step else 0.35
        if gate.arity == 1:
            parts.append(_single_gate(cx, _wire_y(op.targets[0]), op.gate, gate.color, opacity))
        else:
            parts.append(_two_qubit_gate(cx, op, gate.color, opacity))

    if not ops:
        cx = LABEL_W + STEP_W // 2
        parts.append(f'<rect x="{cx - 22}" y="{_wire_y(0) - 22}" width="44" height="44" rx="10" fill="none" '
                     f'stroke="{WIRE}" stroke-width="2" stroke-dasharray="5 4"/>')
        parts.append(f'<text x="{cx + 34}" y="{_wire_y(0) + 1}" dominant-baseline="middle" font-family="{FONT}" '
                     f'font-size="12" fill="{MUTED}">add a gate to begin</text>')
    parts.append("</svg>")
    return "".join(parts)


def _step_label(i: int, ops: List[Operation], n: int) -> str:
    if i == 0:
        return "Start"
    op = ops[i - 1]
    if n == 1:
        return f"{i} · {op.gate}"
    if len(op.targets) == 1:
        return f"{i} · {op.gate} q{op.targets[0]}"
    return f"{i} · {op.gate} q{op.targets[0]}→q{op.targets[1]}"


def render(circuit: Circuit, current_step: int) -> None:
    st.markdown(f'<div style="overflow-x:auto;padding:2px 0 4px 0">{circuit_svg(circuit, current_step)}</div>',
                unsafe_allow_html=True)
    ops = list(circuit.operations)
    if ops:
        choose("Inspect step", list(range(len(ops) + 1)), key="step_control",
               format_func=lambda i: _step_label(i, ops, circuit.num_qubits),
               default=current_step, on_change=model.sync_step_from_control,
               label_visibility="collapsed")
