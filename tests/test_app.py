"""UI smoke tests using Streamlit's headless AppTest harness.

These do not check pixels; they drive the real app script and assert that the
session-state model (qubits, operations, step) and the rendered maths stay in sync.
"""
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import model

APP_PATH = str(Path(__file__).resolve().parent.parent / "app.py")


@pytest.fixture
def app():
    at = AppTest.from_file(APP_PATH, default_timeout=60).run()
    assert not at.exception
    return at


def _button(at, label):
    return next(b for b in at.button if b.label == label)


def _latex_text(at):
    return "\n".join(block.body for block in at.latex)


def test_initial_render_shows_ket0(app):
    assert app.session_state["num_qubits"] == 1
    assert app.session_state["ops"] == []
    assert app.session_state["step"] == 0
    assert r"|\psi_{0}\rangle = |0\rangle" in _latex_text(app)


def test_add_gate_jumps_to_new_step_and_shows_matrix_calculation(app):
    app.button(key="add_H").click().run()
    assert app.session_state["ops"] == [("H", (0,))]
    assert app.session_state["step"] == 1
    text = _latex_text(app)
    assert r"H|\psi_{0}\rangle" in text
    assert r"= |+\rangle" in text
    assert not app.exception


def test_walkthrough_preset_and_step_navigation(app):
    app.selectbox(key="preset_select").select("hzx").run()
    assert app.session_state["ops"] == [("H", (0,)), ("Z", (0,)), ("X", (0,))]
    assert app.session_state["step"] == 3
    assert r"-|-\rangle" in _latex_text(app)

    _button(app, "◀ Previous").click().run()
    assert app.session_state["step"] == 2
    assert r"= |-\rangle" in _latex_text(app)

    _button(app, "Next ▶").click().run()
    assert app.session_state["step"] == 3


def test_undo_and_reset(app):
    app.selectbox(key="preset_select").select("phase_flip").run()
    _button(app, "↶ Undo gate").click().run()
    assert app.session_state["ops"] == [("H", (0,))]
    assert app.session_state["step"] == 1
    _button(app, "Reset").click().run()
    assert app.session_state["ops"] == []
    assert app.session_state["step"] == 0


def test_every_single_qubit_gate_renders_from_every_initial_state(app):
    for initial in ("0", "1", "+", "-"):
        app.session_state["init_0"] = initial
        for symbol in ("H", "X", "Y", "Z", "S", "T"):
            app.button(key=f"add_{symbol}").click().run()
            assert not app.exception, app.exception
        _button(app, "Reset").click().run()


def test_bell_state_preset_uses_two_qubits_and_recognises_phi_plus(app):
    app.selectbox(key="preset_select").select("bell").run()
    assert app.session_state["num_qubits"] == 2
    assert app.session_state["ops"] == [("H", (0,)), ("CNOT", (0, 1))]
    assert r"|\Phi^{+}\rangle" in _latex_text(app)
    assert not app.exception


def test_two_qubit_gates_use_the_selected_control_and_target(app):
    app.selectbox(key="preset_select").select("independent").run()
    app.session_state["ctrl"] = 1
    app.session_state["tgt"] = 0
    app.button(key="add_CNOT").click().run()
    assert app.session_state["ops"][-1] == ("CNOT", (1, 0))
    app.session_state["target"] = 1
    app.button(key="add_T").click().run()
    assert app.session_state["ops"][-1] == ("T", (1,))
    assert not app.exception


def test_measurement_experiment(app):
    app.selectbox(key="preset_select").select("bell").run()
    app.session_state["shots"] = 1000
    app.button(key="measure_button").click().run()
    result = app.session_state["measurement"]
    assert result["shots"] == 1000
    assert sum(result["counts"].values()) == 1000
    assert result["counts"]["01"] == 0 and result["counts"]["10"] == 0
    app.session_state["shots"] = 1
    app.button(key="measure_button").click().run()
    assert app.session_state["measurement"]["outcome"] in ("00", "11")
    # editing the circuit invalidates the result
    app.button(key="add_Z").click().run()
    assert app.session_state["measurement"] is None


def test_three_qubit_ghz_preset(app):
    app.selectbox(key="preset_select").select("ghz").run()
    assert app.session_state["num_qubits"] == 3
    assert r"|000\rangle" in _latex_text(app) and r"|111\rangle" in _latex_text(app)
    assert not app.exception


def test_gate_limit_is_enforced(app):
    for _ in range(12):
        assert not app.button(key="add_X").disabled
        app.button(key="add_X").click().run()
    assert len(app.session_state["ops"]) == 12
    assert app.button(key="add_X").disabled          # no 13th gate
    assert app.session_state["step"] == 12


# --- lesson and practice views -------------------------------------------------------
def _score(at):
    """(correct, answered) computed from the app's session state."""
    from data.practice import QUESTIONS_BY_KEY
    answered = [k for k in at.session_state["checked"] if k in QUESTIONS_BY_KEY]
    correct = sum(1 for k in answered
                  if QUESTIONS_BY_KEY[k].is_correct(at.session_state["answers"].get(k)))
    return correct, len(answered)



def test_all_three_views_render(app):
    for view in model.VIEWS:
        app.session_state["view"] = view
        app.run()
        assert not app.exception, f"{view}: {app.exception}"


def test_lesson_try_it_loads_the_circuit_and_returns_to_explore(app):
    app.session_state["view"] = model.LESSON
    app.run()
    app.button(key="lesson_try_bell_build").click().run()
    assert app.session_state["view"] == model.EXPLORE
    assert app.session_state["num_qubits"] == 2
    assert app.session_state["ops"] == [("H", (0,)), ("CNOT", (0, 1))]
    assert not app.exception


def test_lesson_links_to_practice(app):
    app.session_state["view"] = model.LESSON
    app.run()
    app.button(key="to_practice_bell").click().run()
    assert app.session_state["view"] == model.PRACTICE
    assert app.session_state["active_module"] == "bell"


def test_practice_marks_a_correct_answer(app):
    from data.practice import QUESTIONS
    q = QUESTIONS[0]
    app.session_state["view"] = model.PRACTICE
    app.run()
    app.radio(key=f"choice_{q.key}").set_value(q.answer).run()
    app.button(key=f"check_{q.key}").click().run()
    assert app.session_state["answers"][q.key] == q.answer
    assert _score(app) == (1, 1)
    assert any("Correct" in s.value for s in app.success)


def test_practice_marks_a_wrong_answer_and_allows_retry(app):
    from data.practice import QUESTIONS
    q = QUESTIONS[1]
    wrong = next(o for o in q.options if o != q.answer)
    app.session_state["view"] = model.PRACTICE
    app.run()
    app.radio(key=f"choice_{q.key}").set_value(wrong).run()
    app.button(key=f"check_{q.key}").click().run()
    assert _score(app) == (0, 1)
    assert any("Not quite" in e.value for e in app.error)
    app.button(key=f"retry_{q.key}").click().run()
    assert q.key not in app.session_state["checked"]
    assert _score(app) == (0, 0)


def test_practice_reset_clears_every_answer(app):
    from data.practice import QUESTIONS
    app.session_state["view"] = model.PRACTICE
    app.run()
    for q in QUESTIONS[:3]:
        app.radio(key=f"choice_{q.key}").set_value(q.answer).run()
        app.button(key=f"check_{q.key}").click().run()
    assert _score(app) == (3, 3)
    app.button(key="reset_practice").click().run()
    assert app.session_state["answers"] == {}
    assert _score(app) == (0, 0)


def test_answering_every_question_correctly_scores_full_marks(app):
    from data.practice import QUESTIONS
    app.session_state["view"] = model.PRACTICE
    app.run()
    for q in QUESTIONS:
        app.radio(key=f"choice_{q.key}").set_value(q.answer).run()
        app.button(key=f"check_{q.key}").click().run()
        assert not app.exception, f"{q.key}: {app.exception}"
    assert _score(app) == (len(QUESTIONS), len(QUESTIONS))
    # each module reports its own perfect score
    assert sum("correct" in s.value for s in app.success) >= 8


def test_resetting_one_module_leaves_the_others_untouched(app):
    from data.practice import QUESTIONS, questions_for
    app.session_state["view"] = model.PRACTICE
    app.run()
    for q in QUESTIONS:
        app.radio(key=f"choice_{q.key}").set_value(q.answer).run()
        app.button(key=f"check_{q.key}").click().run()
    app.button(key="reset_qubits").click().run()
    expected = len(QUESTIONS) - len(questions_for("qubits"))
    assert _score(app) == (expected, expected)
    assert not any(q.key in app.session_state["checked"] for q in questions_for("qubits"))


def test_each_lesson_module_can_load_all_of_its_circuits(app):
    from data.curriculum import MODULES
    app.session_state["view"] = model.LESSON
    app.run()
    for module in MODULES:
        for sec in module.sections:
            if sec.circuit is None:
                continue
            app.button(key=f"lesson_try_{module.key}_{sec.key}").click().run()
            assert not app.exception, f"{module.key}/{sec.key}: {app.exception}"
            assert app.session_state["view"] == model.EXPLORE
            assert app.session_state["num_qubits"] == sec.circuit.num_qubits
            app.session_state["view"] = model.LESSON
            app.run()


def test_practice_question_opens_its_circuit_in_explore(app):
    from data.practice import QUESTIONS_BY_KEY
    q = QUESTIONS_BY_KEY["q8_cz"]
    app.session_state["view"] = model.PRACTICE
    app.run()
    app.button(key=f"explore_{q.key}").click().run()
    assert app.session_state["view"] == model.EXPLORE
    assert app.session_state["ops"] == [("CZ", (0, 1))]
    assert app.session_state["init_0"] == "+" and app.session_state["init_1"] == "+"
