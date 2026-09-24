"""The Learn view: one tab per curriculum module."""
from __future__ import annotations

import streamlit as st

import model
from components.circuit import circuit_svg
from components.widgets import section
from data.curriculum import MODULES
from data.lesson import BELL_RECIPES, bell_circuit
from data.practice import questions_for
from quantum.bloch import bloch_vector, length
from utils.format_state import ket_vert, table_cell


def _circuit_preview(spec) -> None:
    """A small, non-interactive picture of the circuit the section is about."""
    circ = spec.to_circuit()
    st.markdown(
        f'<div style="overflow-x:auto;padding:2px 0 6px 0;opacity:.95">'
        f'{circuit_svg(circ, len(circ.operations))}</div>',
        unsafe_allow_html=True,
    )


def _bell_table() -> None:
    rows = ["| Bell state | Definition | Start from | Outcomes |", "|---|---|---|---|"]
    for name, latex, initial in BELL_RECIPES:
        state = bell_circuit(initial).final_state()
        nonzero = [label for label, p in zip(state.basis_labels(), state.probabilities()) if p > 1e-9]
        correlation = "always agree" if all(l[0] == l[1] for l in nonzero) else "always disagree"
        rows.append(
            f"| **{table_cell(name)}** | ${latex.replace('|', chr(92) + 'vert ')}$ | "
            f"${ket_vert(initial[0] + initial[1])}$ | "
            f"{' or '.join(table_cell(f'|{l}⟩') for l in nonzero)} — {correlation} |"
        )
    st.markdown("\n".join(rows))


def _section(sec, module_key: str, index: int) -> None:
    with st.container(border=True):
        section(sec.icon, f"{index}. {sec.title}")
        st.markdown(sec.body)
        for equation in sec.equations:
            st.latex(equation)
        if sec.key == "four":
            _bell_table()
        if sec.circuit is not None:
            _circuit_preview(sec.circuit)
            st.button(
                f"▶ {sec.try_it_label}", key=f"lesson_try_{module_key}_{sec.key}",
                on_click=model.load_circuit_spec,
                args=(sec.circuit, f"**From the lesson — {sec.title}.** {sec.takeaway}"),
                help="Loads this circuit in the Explore view so you can step through it.",
            )
        if sec.takeaway:
            st.success(f"**Takeaway:** {sec.takeaway}", icon="🔑")


def _module_page(module) -> None:
    st.markdown(f"### {module.icon} {module.number}. {module.title}")
    st.caption(module.summary)

    questions = questions_for(module.key)
    correct, answered = model.module_score(module.key)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Sections", len(module.sections))
    with c2:
        st.metric("Practice questions", len(questions))
    with c3:
        st.metric("Your score", f"{correct} / {answered}" if answered else "—",
                  help="Correct answers out of the questions you have checked in this module.")

    for i, sec in enumerate(module.sections, start=1):
        _section(sec, module.key, i)

    with st.container(border=True):
        section("✏️", "Check your understanding",
                f"{len(questions)} questions on {module.title.lower()}, with worked solutions.")
        st.button(f"Practise module {module.number} →", key=f"to_practice_{module.key}",
                  on_click=model.go_to_practice, args=(module.key,), type="primary")


def render() -> None:
    st.markdown("## 📘 Learn")
    st.caption(
        "Eight pages building from a single qubit up to Bell states. Each page ends with practice "
        "questions, and every circuit opens in the Explore view so you can watch it run."
    )
    tabs = st.tabs([m.tab_label for m in MODULES])
    for tab, module in zip(tabs, MODULES):
        with tab:
            _module_page(module)
