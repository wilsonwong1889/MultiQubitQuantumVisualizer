"""UI smoke tests using Streamlit's headless AppTest harness.

These do not check pixels; they drive the real app script and assert that the
session-state model (initial, gates, step) and the rendered maths stay in sync.
"""
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP_PATH = str(Path(__file__).resolve().parent.parent / "app.py")


@pytest.fixture
def app():
    at = AppTest.from_file(APP_PATH, default_timeout=30).run()
    assert not at.exception
    return at


def _button(at, label):
    return next(b for b in at.button if b.label == label)


def _latex_text(at):
    return "\n".join(block.body for block in at.latex)


def test_initial_render_shows_ket0(app):
    assert app.session_state["gates"] == []
    assert app.session_state["step"] == 0
    assert r"|\psi_{0}\rangle = |0\rangle" in _latex_text(app)


def test_add_gate_jumps_to_new_step_and_shows_matrix_calculation(app):
    app.button(key="add_H").click().run()
    assert app.session_state["gates"] == ["H"]
    assert app.session_state["step"] == 1
    text = _latex_text(app)
    assert r"H|\psi_{0}\rangle" in text
    assert r"= |+\rangle" in text
    assert not app.exception


def test_walkthrough_preset_and_step_navigation(app):
    app.button(key="preset_hzx").click().run()
    assert app.session_state["gates"] == ["H", "Z", "X"]
    assert app.session_state["step"] == 3
    assert r"-|-\rangle" in _latex_text(app)

    _button(app, "◀ Previous").click().run()
    assert app.session_state["step"] == 2
    assert r"= |-\rangle" in _latex_text(app)

    app.button(key="circuit_node_1").click().run()      # click the H node
    assert app.session_state["step"] == 1
    assert r"= |+\rangle" in _latex_text(app)

    _button(app, "Next ▶").click().run()
    assert app.session_state["step"] == 2


def test_undo_and_reset(app):
    app.button(key="preset_phase_flip").click().run()
    _button(app, "↶ Undo gate").click().run()
    assert app.session_state["gates"] == ["H"]
    assert app.session_state["step"] == 1
    _button(app, "Reset").click().run()
    assert app.session_state["gates"] == []
    assert app.session_state["step"] == 0


def test_every_initial_state_and_gate_renders_without_error(app):
    for initial in ("0", "1", "+", "-"):
        app.radio(key="initial").set_value(initial).run()
        for symbol in ("H", "X", "Y", "Z"):
            app.button(key=f"add_{symbol}").click().run()
            assert not app.exception, app.exception
        _button(app, "Reset").click().run()


def test_gate_limit_is_enforced(app):
    for _ in range(10):
        assert not app.button(key="add_X").disabled
        app.button(key="add_X").click().run()
    assert len(app.session_state["gates"]) == 10
    assert app.button(key="add_X").disabled          # no 11th gate
    assert app.session_state["step"] == 10
