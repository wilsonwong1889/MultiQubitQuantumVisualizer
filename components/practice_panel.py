"""The Practice view: one tab of questions per curriculum module."""
from __future__ import annotations

import streamlit as st

import model
from components.widgets import section
from data.curriculum import MODULES
from data.practice import QUESTIONS, questions_for

BADGE = {"Warm-up": "🟢", "Core": "🔵", "Challenge": "🟣"}


def _question(q, number: int) -> None:
    s = st.session_state
    answered = q.key in s.checked
    choice = s.answers.get(q.key)
    correct = q.is_correct(choice)

    with st.container(border=True):
        st.markdown(f"**Question {number}** &nbsp; {BADGE[q.difficulty]} {q.difficulty}")
        st.markdown(q.prompt)

        st.radio(
            "Choose one", q.options, key=f"choice_{q.key}", index=None,
            label_visibility="collapsed", disabled=answered,
        )

        c_check, c_retry, c_try = st.columns([1, 1, 2])
        with c_check:
            st.button("Check answer", key=f"check_{q.key}", on_click=model.record_answer,
                      args=(q.key,), disabled=answered or s.get(f"choice_{q.key}") is None,
                      width="stretch")
        with c_retry:
            if answered:
                st.button("Try again", key=f"retry_{q.key}", on_click=model.clear_answer,
                          args=(q.key,), width="stretch")
        with c_try:
            if q.circuit is not None:
                st.button("🔬 Check it in Explore", key=f"explore_{q.key}",
                          on_click=model.load_circuit_spec,
                          args=(q.circuit, f"**From practice question {number}.** Step through it to verify your answer."),
                          help="Loads this question's circuit so you can verify the answer yourself.",
                          width="stretch")

        if not answered:
            if q.hint:
                with st.expander("Need a hint?"):
                    st.markdown(q.hint)
            return

        if correct:
            st.success(f"Correct — **{q.answer}**.", icon="✅")
        else:
            st.error(f"Not quite. You chose **{choice}**; the answer is **{q.answer}**.", icon="❌")
        with st.expander("Worked solution", expanded=not correct):
            st.markdown(q.solution)
            for equation in q.equations:
                st.latex(equation)


def _module_questions(module) -> None:
    questions = questions_for(module.key)
    correct, answered = model.module_score(module.key)
    total = len(questions)

    st.markdown(f"### {module.icon} {module.number}. {module.title}")
    st.caption(module.summary)

    with st.container(border=True):
        c_score, c_bar, c_actions = st.columns([1, 2.4, 1], vertical_alignment="center")
        with c_score:
            st.metric("Score", f"{correct} / {answered}" if answered else "—")
        with c_bar:
            st.progress(answered / total if total else 0.0,
                        text=f"{answered} of {total} questions attempted")
        with c_actions:
            st.button("Reset module", key=f"reset_{module.key}", on_click=model.reset_module,
                      args=(module.key,), disabled=answered == 0, width="stretch")
        if answered == total and total:
            if correct == total:
                st.success(f"Every question in module {module.number} correct. 🎉", icon="🏆")
            else:
                st.info("All attempted — re-read the worked solutions for any you missed, then hit "
                        "*Try again*.", icon="📘")

    for i, q in enumerate(questions, start=1):
        _question(q, i)

    st.button(f"← Back to lesson {module.number}", key=f"back_to_lesson_{module.key}",
              on_click=model.go_to_lesson, args=(module.key,))


def render() -> None:
    st.markdown("## ✏️ Practice")
    correct, answered = model.practice_score()
    total = len(QUESTIONS)
    st.caption(
        f"{total} questions across the eight modules, graded warm-up → challenge. Each one can open its "
        "circuit in Explore so you can verify the answer with the simulator."
    )
    with st.container(border=True):
        c_score, c_bar, c_reset = st.columns([1, 2.4, 1], vertical_alignment="center")
        with c_score:
            st.metric("Overall", f"{correct} / {answered}" if answered else "—",
                      help="Correct answers out of every question you have checked.")
        with c_bar:
            st.progress(answered / total, text=f"{answered} of {total} questions attempted across the course")
        with c_reset:
            st.button("Reset all", key="reset_practice", on_click=model.reset_practice,
                      disabled=answered == 0, width="stretch")

    tabs = st.tabs([m.tab_label for m in MODULES])
    for tab, module in zip(tabs, MODULES):
        with tab:
            _module_questions(module)
