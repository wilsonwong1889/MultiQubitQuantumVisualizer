"""Practice questions with checked answers and worked solutions."""
from __future__ import annotations

import streamlit as st

import model
from components.widgets import section
from data.practice import DIFFICULTIES, QUESTIONS

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


def render() -> None:
    st.markdown("## ✏️ Practice")
    st.caption(
        "Ten questions on Bell states, entanglement and measurement. Answer, check, and read the "
        "worked solution — or open any question's circuit in Explore and verify it with the simulator."
    )

    correct, answered = model.practice_score()
    total = len(QUESTIONS)
    with st.container(border=True):
        c_score, c_bar, c_reset = st.columns([1, 2.4, 1], vertical_alignment="center")
        with c_score:
            st.metric("Score", f"{correct} / {answered}" if answered else "—",
                      help="Correct answers out of the questions you have checked.")
        with c_bar:
            st.progress(answered / total, text=f"{answered} of {total} questions attempted")
        with c_reset:
            st.button("Reset answers", key="reset_practice", on_click=model.reset_practice,
                      disabled=answered == 0, width="stretch")
        if answered == total:
            if correct == total:
                st.success("Every question correct — you have Bell states down. 🎉", icon="🏆")
            else:
                st.info("All questions attempted. Re-read the worked solutions for any you missed, "
                        "then hit *Try again*.", icon="📘")

    number = 0
    for difficulty in DIFFICULTIES:
        questions = [q for q in QUESTIONS if q.difficulty == difficulty]
        if not questions:
            continue
        st.markdown(f"### {BADGE[difficulty]} {difficulty}")
        for q in questions:
            number += 1
            _question(q, number)

    st.button("← Back to the lesson", key="practice_to_lesson",
              on_click=model.go_to, args=(model.LESSON,))
