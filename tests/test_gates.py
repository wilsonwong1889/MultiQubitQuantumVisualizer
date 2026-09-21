import math

import pytest

from quantum.gates import GATE_ORDER, GATES, H, X, Y, Z, get_gate
from quantum.matrix import IDENTITY


@pytest.mark.parametrize("gate", [X, Y, Z, H])
def test_every_gate_is_unitary(gate):
    assert gate.matrix.is_unitary()


@pytest.mark.parametrize("gate", [X, Y, Z, H])
def test_every_gate_squares_to_identity(gate):
    # X^2 = Y^2 = Z^2 = H^2 = I
    assert gate.matrix.multiply(gate.matrix).is_close(IDENTITY)


def test_display_factorisation_matches_real_matrix():
    for gate in GATES.values():
        shown = gate.shown_matrix.scale(gate.display_scale)
        assert shown.is_close(gate.matrix)


def test_rotation_axes_are_unit_vectors_and_half_turns():
    for gate in GATES.values():
        assert math.isclose(sum(c * c for c in gate.axis), 1.0, abs_tol=1e-12)
        assert math.isclose(gate.rotation, math.pi)


def test_gate_lookup():
    assert [get_gate(s).symbol for s in GATE_ORDER] == ["H", "X", "Y", "Z"]
    with pytest.raises(KeyError):
        get_gate("CNOT")
